from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evaluate_aistap_target_preservation_ablation import load_trainable_model


def to_complex(arr: np.ndarray) -> np.ndarray:
    if arr.dtype.fields and {"real", "imag"} <= set(arr.dtype.fields):
        return arr["real"] + 1j * arr["imag"]
    return np.asarray(arr)


def decode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.ndarray):
        if value.size == 1:
            return decode_value(value.reshape(-1)[0])
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def read_meta(f: h5py.File, ref: Any) -> dict[str, Any]:
    grp = f[ref]
    return {key: decode_value(grp[key][()]) for key in grp.keys()}


def score_map(x: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(x) ** 2, axis=0)


def conservative_cfar_threshold(bg: np.ndarray, pfa: float) -> tuple[float, int]:
    bg = np.asarray(bg).reshape(-1)
    if bg.size == 0:
        return float("nan"), 0
    max_false_alarms = int(np.floor(float(pfa) * bg.size))
    if max_false_alarms <= 0:
        return float(np.max(bg)), 0
    if max_false_alarms >= bg.size:
        return float(np.nextafter(np.min(bg), -np.inf)), int(bg.size)
    threshold_index = bg.size - max_false_alarms - 1
    threshold = float(np.partition(bg, threshold_index)[threshold_index])
    return threshold, max_false_alarms


def target_mask(meta: dict[str, Any], shape: tuple[int, int]) -> np.ndarray:
    try:
        ntrue = float(np.asarray(meta.get("Ntrue", 0.0)).reshape(-1)[0])
    except Exception:
        ntrue = 0.0
    if ntrue <= 0:
        return np.zeros(shape, dtype=bool)

    dop_axis = np.asarray(meta["truth_pix_dop_axis"]).reshape(-1)
    range_axis = np.asarray(meta["truth_pix_range_axis"]).reshape(-1)
    dop_vals = np.rint(np.asarray(meta["targ_pix_dop"]).reshape(-1)).astype(int)
    range_vals = np.rint(np.asarray(meta["targ_pix_range"]).reshape(-1)).astype(int)
    dop_min = int(dop_axis.min())
    range_min = int(range_axis.min())
    mask = np.zeros(shape, dtype=bool)
    for d, r in zip(dop_vals, range_vals):
        di = d - dop_min
        ri = r - range_min
        if 0 <= di < shape[0] and 0 <= ri < shape[1]:
            mask[di, ri] = True
    return mask


def summarize(score: np.ndarray, mask: np.ndarray, pfas: list[float]) -> list[dict[str, Any]]:
    bg = score[~mask]
    tgt = score[mask]
    rows: list[dict[str, Any]] = []
    for pfa in pfas:
        threshold, max_false_alarms = conservative_cfar_threshold(bg, pfa)
        det = score > threshold
        false_alarms = int(det[~mask].sum()) if bg.size else 0
        rows.append(
            {
                "pfa_target": float(pfa),
                "threshold": threshold,
                "pd": float(det[mask].mean()) if tgt.size else float("nan"),
                "empirical_pfa": float(det[~mask].mean()) if bg.size else float("nan"),
                "target_count": int(tgt.size),
                "background_count": int(bg.size),
                "max_false_alarms": int(max_false_alarms),
                "false_alarms": false_alarms,
                "detections": int(det.sum()),
                "threshold_policy": "conservative_topk_strict_gt",
            }
        )
    return rows


def summarize_finished_detector(
    residual_score: np.ndarray, gate_score: np.ndarray, mask: np.ndarray, pfas: list[float]
) -> list[dict[str, Any]]:
    residual_bg = residual_score[~mask]
    gate_bg = gate_score[~mask]
    tgt = residual_score[mask]
    rows: list[dict[str, Any]] = []
    gate_threshold, gate_max_false_alarms = conservative_cfar_threshold(gate_bg, 0.0)
    gate_det = gate_score > gate_threshold
    for pfa in pfas:
        residual_threshold, residual_max_false_alarms = conservative_cfar_threshold(residual_bg, pfa)
        residual_det = residual_score > residual_threshold
        det = residual_det | gate_det
        false_alarms = int(det[~mask].sum()) if residual_bg.size else 0
        rows.append(
            {
                "pfa_target": float(pfa),
                "threshold": float("nan"),
                "residual_threshold": residual_threshold,
                "gate_threshold": gate_threshold,
                "pd": float(det[mask].mean()) if tgt.size else float("nan"),
                "empirical_pfa": float(det[~mask].mean()) if residual_bg.size else float("nan"),
                "target_count": int(tgt.size),
                "background_count": int(residual_bg.size),
                "max_false_alarms": int(residual_max_false_alarms + gate_max_false_alarms),
                "false_alarms": false_alarms,
                "detections": int(det.sum()),
                "threshold_policy": "residual_cfar_plus_zero_false_gate_union",
            }
        )
    return rows


def evaluate(asset_path: Path, state_path: Path, pfas: list[float], max_positive: int | None) -> tuple[pd.DataFrame, dict[str, Any]]:
    model = load_trainable_model(state_path)
    model.eval()
    rows: list[dict[str, Any]] = []
    total_frames = 0
    positive_frames = 0
    evaluated_positive = 0

    with h5py.File(asset_path, "r") as f, torch.no_grad():
        refs = f["meta_per_image"][()].reshape(-1)
        total_frames = int(len(refs))
        for idx, ref in enumerate(refs):
            meta = read_meta(f, ref)
            x_np = to_complex(f["rd_img"][idx])
            mask = target_mask(meta, score_map(x_np).shape)
            if not mask.any():
                continue
            positive_frames += 1
            if max_positive is not None and evaluated_positive >= max_positive:
                continue
            x = torch.from_numpy(x_np).to(torch.complex128)
            out = model(x)
            raw_score = score_map(x_np)
            residual_score = score_map(out["residual"].detach().cpu().numpy())
            gate_score = out["score"].detach().cpu().numpy()
            item_id = f"{asset_path.name}#{idx}"
            method_rows: list[tuple[str, list[dict[str, Any]]]] = []
            for method, score in [
                ("raw", raw_score),
                (f"low_rank_residual_k{model.rank}", residual_score),
                ("tpsscs_trainable_gate", gate_score),
            ]:
                method_rows.append((method, summarize(score, mask, pfas)))
            method_rows.append(
                (
                    "tpsscs_finished_detector",
                    summarize_finished_detector(residual_score, gate_score, mask, pfas),
                )
            )
            for method, method_summary in method_rows:
                for row in method_summary:
                    row.update(
                        {
                            "asset": asset_path.name,
                            "image_index": idx,
                            "item_id": item_id,
                            "method": method,
                        }
                    )
                    rows.append(row)
            evaluated_positive += 1

    info = {
        "asset": str(asset_path),
        "state": str(state_path),
        "total_frames": total_frames,
        "positive_frames": positive_frames,
        "evaluated_positive_frames": evaluated_positive,
    }
    return pd.DataFrame(rows), info


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "绗笁鎵?"))
    parser.add_argument("--asset", default="data/downloads/aistap_sim/full/simMed_test.mat")
    parser.add_argument("--state", default="results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt")
    parser.add_argument("--max-positive", type=int, default=128)
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--tag", default="20260715")
    args = parser.parse_args()

    root = Path(args.root)
    asset = Path(args.asset)
    if not asset.is_absolute():
        asset = root / asset
    state = Path(args.state)
    if not state.is_absolute():
        state = root / state
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    max_positive = None if args.max_positive <= 0 else args.max_positive

    df, info = evaluate(asset, state, pfas, max_positive)
    result_dir = root / "results" / "aistap_full_asset"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    csv_path = result_dir / f"aistap_full_asset_detector_candidate_{asset.stem}_{args.tag}.csv"
    json_path = result_dir / f"aistap_full_asset_detector_candidate_{asset.stem}_{args.tag}.json"
    note_path = log_dir / f"aistap_full_asset_detector_candidate_{asset.stem}_{args.tag}.md"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    summary = (
        df.groupby(["method", "pfa_target"])
        .agg(
            pd_mean=("pd", "mean"),
            pd_std=("pd", "std"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
        if not df.empty
        else pd.DataFrame()
    )
    json_path.write_text(
        json.dumps({**info, "summary": summary.to_dict(orient="records")}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# AISTAP Full-Asset Detector Candidate Evaluation",
        "",
        f"Date: {args.tag}",
        "",
        "## Setup",
        "",
        f"- Asset: `{asset}`",
        f"- State: `{state}`",
        f"- Total frames: `{info['total_frames']}`",
        f"- Target-bearing frames in asset: `{info['positive_frames']}`",
        f"- Evaluated target-bearing frames: `{info['evaluated_positive_frames']}`",
        "- CFAR threshold policy: `conservative_topk_strict_gt` (`score > threshold`; per-frame false alarms are capped at `floor(Pfa * background_count)`).",
        "- Finished detector policy: `residual_cfar_plus_zero_false_gate_union` (rank-matched residual CFAR plus a trainable-gate head that is admitted only above its background maximum).",
        "",
        "## Detection Summary",
        "",
        "| Method | Pfa | Pd mean | Pd std | Empirical Pfa mean | Items |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.sort_values(["method", "pfa_target"]).iterrows():
        lines.append(
            f"| {row['method']} | {row['pfa_target']:.0e} | {row['pd_mean']:.4f} | {row['pd_std']:.4f} | {row['empirical_pfa_mean']:.4f} | {int(row['n_items'])} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is an official AISTAP-SIM full test asset, not only the small sample bundle.",
            "- It improves the sample-scale evidence for the saved detector candidate.",
            "- It remains in-domain AISTAP-SIM evidence, not independent external-dataset validation.",
        ]
    )
    note_path.write_text("\n".join(lines), encoding="utf-8")

    print(csv_path)
    print(json_path)
    print(note_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

