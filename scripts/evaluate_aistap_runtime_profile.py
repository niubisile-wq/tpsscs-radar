from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import h5py
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import evaluate_aistap_full_asset_candidate as candidate
import evaluate_aistap_full_asset_loso_feature_ensemble_baseline as hgb_base
from evaluate_aistap_target_preservation_ablation import load_trainable_model


@dataclass
class FrameRecord:
    asset: str
    image_index: int
    target_pixels: int
    background_pixels: int
    shape: str
    channels: int
    doppler_bins: int
    range_bins: int


def parse_paths(text: str) -> list[Path]:
    return [Path(x.strip()) for x in text.split(",") if x.strip()]


def resolve_under_root(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def timed_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def count_params(model: torch.nn.Module) -> int:
    return int(sum(p.numel() for p in model.parameters()))


def gate_score_from_residual(model: torch.nn.Module, x: torch.Tensor, residual: torch.Tensor) -> dict[str, torch.Tensor]:
    raw_score = torch.sum(torch.abs(x) ** 2, dim=0, keepdim=True).float()
    resid_score = torch.sum(torch.abs(residual) ** 2, dim=0, keepdim=True).float()
    feats = torch.cat([torch.log1p(raw_score), torch.log1p(resid_score)], dim=0).unsqueeze(0)
    gate_logits = model.gate_net(feats).squeeze(0).squeeze(0)
    gate = torch.sigmoid(gate_logits)
    gate_c = gate.to(x.dtype)[None, :, :]
    enhanced = gate_c * x + (1.0 - gate_c) * residual
    score = torch.sum(torch.abs(enhanced) ** 2, dim=0)
    return {"gate": gate, "score": score}


def target_frame_indices(asset_path: Path, max_frames: int) -> list[int]:
    positive: list[int] = []
    with h5py.File(asset_path, "r") as f:
        refs = f["meta_per_image"][()].reshape(-1)
        for idx, ref in enumerate(refs):
            meta = candidate.read_meta(f, ref)
            x_shape = f["rd_img"][idx].shape
            mask_shape = (int(x_shape[1]), int(x_shape[2]))
            if candidate.target_mask(meta, mask_shape).any():
                positive.append(idx)
    if max_frames <= 0 or len(positive) <= max_frames:
        return positive
    sample_positions = np.linspace(0, len(positive) - 1, max_frames)
    picked = sorted({positive[int(round(pos))] for pos in sample_positions})
    cursor = 0
    while len(picked) < max_frames and cursor < len(positive):
        if positive[cursor] not in picked:
            picked.append(positive[cursor])
        cursor += 1
    return sorted(picked[:max_frames])


def load_frame(asset_path: Path, image_index: int) -> tuple[np.ndarray, np.ndarray, FrameRecord]:
    with h5py.File(asset_path, "r") as f:
        refs = f["meta_per_image"][()].reshape(-1)
        meta = candidate.read_meta(f, refs[image_index])
        x_np = candidate.to_complex(f["rd_img"][image_index])
        mask = candidate.target_mask(meta, candidate.score_map(x_np).shape)
    record = FrameRecord(
        asset=asset_path.name,
        image_index=int(image_index),
        target_pixels=int(mask.sum()),
        background_pixels=int((~mask).sum()),
        shape="x".join(str(v) for v in x_np.shape),
        channels=int(x_np.shape[0]),
        doppler_bins=int(x_np.shape[1]),
        range_bins=int(x_np.shape[2]),
    )
    return x_np, mask, record


def train_hgb_profiles(
    assets: list[Path],
    rank: int,
    train_max_frames: int,
    background_per_frame: int,
    seed: int,
    hgb_max_iter: int,
    hgb_learning_rate: float,
    hgb_max_leaf_nodes: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = np.random.default_rng(seed)
    models: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    infos: list[dict[str, Any]] = []
    if len(assets) < 2:
        return models, rows, infos

    for test_asset in assets:
        train_asset = next(asset for asset in assets if asset != test_asset)
        (x_train, y_train, weights, info), sample_seconds = timed_call(
            lambda train_asset=train_asset: hgb_base.collect_training_samples(
                train_asset,
                rng,
                rank=rank,
                background_per_frame=background_per_frame,
                max_frames=train_max_frames if train_max_frames > 0 else None,
            )
        )
        model, fit_seconds = timed_call(
            lambda: hgb_base.train_hgb(
                x_train,
                y_train,
                weights,
                max_iter=hgb_max_iter,
                learning_rate=hgb_learning_rate,
                max_leaf_nodes=hgb_max_leaf_nodes,
                l2_regularization=0.0,
                seed=seed,
            )
        )
        models[test_asset.name] = model
        info.test_asset = test_asset.name
        info_dict = asdict(info)
        info_dict.update(
            {
                "feature_dim": int(x_train.shape[1]),
                "samples": int(x_train.shape[0]),
                "positive_samples": int(np.sum(y_train == 1)),
                "background_samples": int(np.sum(y_train == 0)),
                "hgb_max_iter": int(hgb_max_iter),
                "hgb_effective_iter": int(getattr(model, "n_iter_", hgb_max_iter)),
                "hgb_max_leaf_nodes": int(hgb_max_leaf_nodes),
            }
        )
        infos.append(info_dict)
        for component, seconds in [
            ("hgb_training_sample_collection", sample_seconds),
            ("hgb_fit", fit_seconds),
        ]:
            rows.append(
                {
                    "asset": test_asset.name,
                    "image_index": -1,
                    "component": component,
                    "seconds": seconds,
                    "milliseconds": seconds * 1000.0,
                    "scope": f"train_on_{train_asset.name}_for_test_{test_asset.name}",
                    "target_pixels": np.nan,
                    "background_pixels": np.nan,
                    "shape": "",
                }
            )
    return models, rows, infos


def profile_frame(
    x_np: np.ndarray,
    mask: np.ndarray,
    record: FrameRecord,
    model: torch.nn.Module,
    hgb_model: Any | None,
    rank: int,
    pfas: list[float],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    totals: dict[str, float] = {}

    def add(component: str, seconds: float, scope: str = "per_frame") -> None:
        rows.append(
            {
                "asset": record.asset,
                "image_index": record.image_index,
                "component": component,
                "seconds": seconds,
                "milliseconds": seconds * 1000.0,
                "scope": scope,
                "target_pixels": record.target_pixels,
                "background_pixels": record.background_pixels,
                "shape": record.shape,
            }
        )
        totals[component] = seconds

    raw_score, seconds = timed_call(lambda: candidate.score_map(x_np))
    add("raw_score_numpy", seconds)

    numpy_residual_score, seconds = timed_call(lambda: hgb_base.low_rank_residual_score(x_np, rank))
    add("numpy_rank30_residual_score", seconds)

    x_torch = torch.from_numpy(x_np).to(torch.complex128)
    with torch.no_grad():
        residual, seconds = timed_call(lambda: model.low_rank(x_torch)[0])
        add("tpsscs_low_rank_torch", seconds)

        _, seconds = timed_call(lambda: gate_score_from_residual(model, x_torch, residual))
        add("tpsscs_gate_and_enhanced_score_after_residual", seconds)

        def run_tpsscs_materialized() -> tuple[np.ndarray, np.ndarray]:
            out = model(x_torch)
            return candidate.score_map(out["residual"].detach().cpu().numpy()), out["score"].detach().cpu().numpy()

        (residual_score, tpsscs_score), seconds = timed_call(run_tpsscs_materialized)
        add("tpsscs_total_forward_materialized", seconds)

    _, seconds = timed_call(lambda: candidate.summarize_finished_detector(residual_score, tpsscs_score, mask, pfas))
    add("finished_detector_thresholds_7pfa", seconds)

    if hgb_model is not None:
        hgb_feats, seconds = timed_call(
            lambda: hgb_base.feature_cube(raw_score, numpy_residual_score).reshape(-1, len(hgb_base.FEATURE_NAMES))
        )
        add("raw_residual_hgb_feature_cube", seconds)
        _, seconds = timed_call(lambda: hgb_model.predict_proba(hgb_feats)[:, 1])
        add("raw_residual_hgb_predict_proba", seconds)

    total_rows = [
        {
            **asdict(record),
            "profile": "compact_tpsscs_finished_detector",
            "seconds": totals.get("tpsscs_total_forward_materialized", 0.0)
            + totals.get("finished_detector_thresholds_7pfa", 0.0),
            "milliseconds": (
                totals.get("tpsscs_total_forward_materialized", 0.0)
                + totals.get("finished_detector_thresholds_7pfa", 0.0)
            )
            * 1000.0,
        },
        {
            **asdict(record),
            "profile": "raw_residual_hgb_inference",
            "seconds": totals.get("raw_score_numpy", 0.0)
            + totals.get("numpy_rank30_residual_score", 0.0)
            + totals.get("raw_residual_hgb_feature_cube", 0.0)
            + totals.get("raw_residual_hgb_predict_proba", 0.0),
            "milliseconds": (
                totals.get("raw_score_numpy", 0.0)
                + totals.get("numpy_rank30_residual_score", 0.0)
                + totals.get("raw_residual_hgb_feature_cube", 0.0)
                + totals.get("raw_residual_hgb_predict_proba", 0.0)
            )
            * 1000.0,
        },
        {
            **asdict(record),
            "profile": "shared_low_rank_numpy_plus_hgb_features",
            "seconds": totals.get("numpy_rank30_residual_score", 0.0)
            + totals.get("raw_residual_hgb_feature_cube", 0.0),
            "milliseconds": (
                totals.get("numpy_rank30_residual_score", 0.0)
                + totals.get("raw_residual_hgb_feature_cube", 0.0)
            )
            * 1000.0,
        },
        {
            **asdict(record),
            "profile": "tpsscs_gate_head_after_low_rank",
            "seconds": totals.get("tpsscs_gate_and_enhanced_score_after_residual", 0.0),
            "milliseconds": totals.get("tpsscs_gate_and_enhanced_score_after_residual", 0.0) * 1000.0,
        },
    ]
    return rows, total_rows


def aggregate(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    return (
        df.groupby(group_cols, dropna=False)
        .agg(
            n=("milliseconds", "count"),
            median_ms=("milliseconds", "median"),
            mean_ms=("milliseconds", "mean"),
            p25_ms=("milliseconds", lambda s: float(np.quantile(s, 0.25))),
            p75_ms=("milliseconds", lambda s: float(np.quantile(s, 0.75))),
            p95_ms=("milliseconds", lambda s: float(np.quantile(s, 0.95))),
            min_ms=("milliseconds", "min"),
            max_ms=("milliseconds", "max"),
        )
        .reset_index()
    )


def write_markdown(
    path: Path,
    date_tag: str,
    payload: dict[str, Any],
    component_summary: pd.DataFrame,
    profile_summary: pd.DataFrame,
    hgb_train_summary: pd.DataFrame,
) -> None:
    lines = [
        "# AISTAP Runtime And Complexity Profile",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Timed target-bearing frames: `{payload['timed_target_frames_total']}` across `{len(payload['assets'])}` official full assets.",
        f"- Compact TP-SSCS finished-detector median inference time: `{payload['compact_tpsscs_finished_detector_median_ms']:.2f}` ms/frame.",
        f"- Raw/residual HGB median inference time: `{payload['raw_residual_hgb_inference_median_ms']:.2f}` ms/frame.",
        f"- HGB/compact median runtime ratio: `{payload['hgb_over_compact_runtime_ratio']:.2f}x`.",
        f"- Trainable TP-SSCS parameter count: `{payload['tpsscs_parameter_count']}`.",
        f"- Raw/residual HGB feature dimension: `{payload['raw_residual_hgb_feature_dim']}`.",
        f"- Main interpretation: `{payload['interpretation']}`",
        "",
        "## End-to-End Inference Profiles",
        "",
        "| Profile | n | Median ms | Mean ms | P25-P75 ms | P95 ms |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in profile_summary.sort_values("profile").iterrows():
        lines.append(
            f"| `{row['profile']}` | {int(row['n'])} | {row['median_ms']:.2f} | {row['mean_ms']:.2f} | "
            f"{row['p25_ms']:.2f}-{row['p75_ms']:.2f} | {row['p95_ms']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Component Timings",
            "",
            "| Component | n | Median ms | Mean ms | P95 ms |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in component_summary.sort_values("median_ms", ascending=False).iterrows():
        lines.append(
            f"| `{row['component']}` | {int(row['n'])} | {row['median_ms']:.2f} | {row['mean_ms']:.2f} | {row['p95_ms']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## HGB Training Cost Boundary",
            "",
            "| Scope | Component | Median ms | Mean ms |",
            "|---|---|---:|---:|",
        ]
    )
    for _, row in hgb_train_summary.sort_values(["scope", "component"]).iterrows():
        lines.append(f"| `{row['scope']}` | `{row['component']}` | {row['median_ms']:.2f} | {row['mean_ms']:.2f} |")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a CPU runtime profile on the local machine, not a hardware-independent speed benchmark.",
            "- The timing audit supports a bounded deployment-cost claim: the compact detector uses a small gate and no supervised HGB inference stack, while the dominant cost remains low-rank residual formation.",
            "- The result should not be used to claim universal real-time performance or speed superiority on other hardware.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--assets",
        default="data/downloads/aistap_sim/full/simMed_test.mat,data/downloads/aistap_sim/full/simWind_test.mat",
    )
    parser.add_argument("--state", default="results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--rank", type=int, default=30)
    parser.add_argument("--timed-frames-per-asset", type=int, default=24)
    parser.add_argument("--train-max-frames", type=int, default=64)
    parser.add_argument("--background-per-frame", type=int, default=256)
    parser.add_argument("--hgb-max-iter", type=int, default=100)
    parser.add_argument("--hgb-learning-rate", type=float, default=0.05)
    parser.add_argument("--hgb-max-leaf-nodes", type=int, default=31)
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--torch-threads", type=int, default=0)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    assets = [resolve_under_root(root, p) for p in parse_paths(args.assets)]
    state = resolve_under_root(root, Path(args.state))
    pfas = [float(x.strip()) for x in args.pfas.split(",") if x.strip()]
    if args.torch_threads > 0:
        torch.set_num_threads(args.torch_threads)

    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    model = load_trainable_model(state)
    model.eval()
    hgb_models, train_rows, hgb_infos = train_hgb_profiles(
        assets=assets,
        rank=args.rank,
        train_max_frames=args.train_max_frames,
        background_per_frame=args.background_per_frame,
        seed=args.seed,
        hgb_max_iter=args.hgb_max_iter,
        hgb_learning_rate=args.hgb_learning_rate,
        hgb_max_leaf_nodes=args.hgb_max_leaf_nodes,
    )

    component_rows: list[dict[str, Any]] = []
    component_rows.extend(train_rows)
    total_rows: list[dict[str, Any]] = []
    frame_records: list[dict[str, Any]] = []

    for asset in assets:
        for idx in target_frame_indices(asset, args.timed_frames_per_asset):
            x_np, mask, record = load_frame(asset, idx)
            frame_records.append(asdict(record))
            rows, totals = profile_frame(
                x_np=x_np,
                mask=mask,
                record=record,
                model=model,
                hgb_model=hgb_models.get(asset.name),
                rank=args.rank,
                pfas=pfas,
            )
            component_rows.extend(rows)
            total_rows.extend(totals)

    component_df = pd.DataFrame(component_rows)
    totals_df = pd.DataFrame(total_rows)
    frames_df = pd.DataFrame(frame_records)
    component_summary = aggregate(
        component_df[component_df["scope"].eq("per_frame")].copy(),
        ["component"],
    )
    profile_summary = aggregate(totals_df.copy(), ["profile"])
    hgb_train_summary = aggregate(
        component_df[component_df["scope"].str.startswith("train_on_", na=False)].copy(),
        ["scope", "component"],
    )

    profile_lookup = profile_summary.set_index("profile")["median_ms"].to_dict()
    compact_median = float(profile_lookup.get("compact_tpsscs_finished_detector", float("nan")))
    hgb_median = float(profile_lookup.get("raw_residual_hgb_inference", float("nan")))
    ratio = float(hgb_median / compact_median) if np.isfinite(compact_median) and compact_median > 0 else float("nan")
    if np.isfinite(ratio) and ratio >= 1.0:
        interpretation = "compact_inference_no_slower_than_raw_residual_hgb_on_this_cpu_profile"
    else:
        interpretation = "compact_runtime_boundary_dominant_cost_is_low_rank_not_gate_head"

    payload: dict[str, Any] = {
        "date": args.date,
        "root": ".",
        "assets": [asset.name for asset in assets],
        "state": args.state,
        "rank": int(args.rank),
        "timed_frames_per_asset": int(args.timed_frames_per_asset),
        "timed_target_frames_total": int(len(frames_df)),
        "profile_scope": "deterministic_target_bearing_frame_sample_across_official_full_assets",
        "pfas": pfas,
        "compact_tpsscs_finished_detector_median_ms": compact_median,
        "raw_residual_hgb_inference_median_ms": hgb_median,
        "hgb_over_compact_runtime_ratio": ratio,
        "tpsscs_parameter_count": count_params(model),
        "raw_residual_hgb_feature_dim": int(len(hgb_base.FEATURE_NAMES)),
        "hgb_training_profiles": hgb_infos,
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "torch_version": torch.__version__,
        "torch_num_threads": int(torch.get_num_threads()),
        "numpy_version": np.__version__,
        "interpretation": interpretation,
        "boundary": [
            "local_cpu_runtime_profile_not_hardware_independent_speed_benchmark",
            "supports_bounded_deployment_cost_claim_only",
            "does_not_claim_universal_real_time_performance",
        ],
    }

    component_csv = result_dir / f"aistap_runtime_profile_components_{args.date}.csv"
    totals_csv = result_dir / f"aistap_runtime_profile_totals_{args.date}.csv"
    frames_csv = result_dir / f"aistap_runtime_profile_frames_{args.date}.csv"
    summary_csv = result_dir / f"aistap_runtime_profile_summary_{args.date}.csv"
    json_path = result_dir / f"aistap_runtime_profile_{args.date}.json"
    md_path = log_dir / f"aistap_runtime_profile_{args.date}.md"

    component_df.to_csv(component_csv, index=False, encoding="utf-8-sig")
    totals_df.to_csv(totals_csv, index=False, encoding="utf-8-sig")
    frames_df.to_csv(frames_csv, index=False, encoding="utf-8-sig")
    pd.concat(
        [
            component_summary.assign(summary_type="component"),
            profile_summary.assign(summary_type="profile"),
            hgb_train_summary.assign(summary_type="hgb_training"),
        ],
        ignore_index=True,
        sort=False,
    ).to_csv(summary_csv, index=False, encoding="utf-8-sig")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, args.date, payload, component_summary, profile_summary, hgb_train_summary)

    print(md_path)
    print(json_path)
    print(summary_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
