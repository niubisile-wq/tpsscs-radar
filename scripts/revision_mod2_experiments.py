from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SRC = ROOT / "src"
for p in [SCRIPTS, SRC]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from evaluate_aistap_full_asset_candidate import (  # noqa: E402
    conservative_cfar_threshold,
    read_meta,
    score_map,
    summarize,
    target_mask,
    to_complex,
)
from evaluate_aistap_target_preservation_ablation import load_trainable_model  # noqa: E402
from evaluate_ipix_validated_residual_fusion import (  # noqa: E402
    fusion_score as ipix_fusion_score,
    load_items as load_ipix_items,
)
from evaluate_ipix_external_detector_transfer import summarize_score as summarize_ipix_score  # noqa: E402
from evaluate_ssdd_external_trainable_gate import (  # noqa: E402
    PFAS as SSDD_PFAS,
    collect_split,
    load_coco,
    policy_scores,
    sample_development,
    split_train_ids,
)
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402


OUT = ROOT / "results" / "revision_enhancement_20260722"
PFAS = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
IPIX_PFAS = PFAS


def eval_score(score: np.ndarray, mask: np.ndarray, pfas: list[float] = PFAS) -> list[dict[str, Any]]:
    return summarize(score, mask, pfas)


def eval_detector_union(residual_score: np.ndarray, gate_score: np.ndarray, mask: np.ndarray) -> list[dict[str, Any]]:
    residual_bg = residual_score[~mask]
    gate_bg = gate_score[~mask]
    gate_threshold, gate_false = conservative_cfar_threshold(gate_bg, 0.0)
    gate_det = gate_score > gate_threshold
    rows: list[dict[str, Any]] = []
    for pfa in PFAS:
        residual_threshold, residual_false = conservative_cfar_threshold(residual_bg, pfa)
        residual_det = residual_score > residual_threshold
        det = residual_det | gate_det
        rows.append(
            {
                "pfa_target": pfa,
                "threshold": np.nan,
                "pd": float(det[mask].mean()),
                "empirical_pfa": float(det[~mask].mean()),
                "target_count": int(mask.sum()),
                "background_count": int((~mask).sum()),
                "max_false_alarms": int(residual_false + gate_false),
                "false_alarms": int(det[~mask].sum()),
                "detections": int(det[mask].sum()),
                "threshold_policy": "residual_cfar_plus_zero_false_gate_union",
                "residual_threshold": residual_threshold,
                "gate_threshold": gate_threshold,
            }
        )
    return rows


def aistap_fixed_fusion_and_bootstrap() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    state = ROOT / "results" / "aistap_sample" / "tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt"
    model = load_trainable_model(state)
    model.eval()
    assets = [
        ROOT / "data" / "downloads" / "aistap_sim" / "full" / "simMed_test.mat",
        ROOT / "data" / "downloads" / "aistap_sim" / "full" / "simWind_test.mat",
    ]
    rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    with torch.no_grad():
        for asset in assets:
            with h5py.File(asset, "r") as f:
                refs = f["meta_per_image"][()].reshape(-1)
                for idx, ref in enumerate(refs):
                    meta = read_meta(f, ref)
                    x_np = to_complex(f["rd_img"][idx])
                    mask = target_mask(meta, score_map(x_np).shape)
                    if not mask.any():
                        continue
                    x = torch.from_numpy(x_np).to(torch.complex128)
                    out = model(x)
                    raw = score_map(x_np)
                    residual = score_map(out["residual"].detach().cpu().numpy())
                    gate = out["score"].detach().cpu().numpy()
                    item_id = f"{asset.name}#{idx}"
                    for method, score in [
                        ("raw", raw),
                        (f"low_rank_residual_k{model.rank}", residual),
                        ("tpsscs_trainable_gate_score", gate),
                    ]:
                        for row in eval_score(score, mask):
                            row.update({"asset": asset.name, "image_index": idx, "item_id": item_id, "method": method})
                            rows.append(row)
                    for row in eval_detector_union(residual, gate, mask):
                        row.update({"asset": asset.name, "image_index": idx, "item_id": item_id, "method": "tpsscs_adaptive_gate"})
                        rows.append(row)
                    for w in np.round(np.linspace(0.0, 1.0, 21), 2):
                        fixed = float(w) * residual + (1.0 - float(w)) * raw
                        for row in eval_score(fixed, mask):
                            row.update(
                                {
                                    "asset": asset.name,
                                    "image_index": idx,
                                    "item_id": item_id,
                                    "method": "fixed_weight_fusion",
                                    "w_residual": float(w),
                                }
                            )
                            rows.append(row)
                    score_rows.append(
                        {
                            "asset": asset.name,
                            "image_index": idx,
                            "item_id": item_id,
                            "raw_target_mean": float(raw[mask].mean()),
                            "raw_background_mean": float(raw[~mask].mean()),
                            "residual_target_mean": float(residual[mask].mean()),
                            "residual_background_mean": float(residual[~mask].mean()),
                            "gate_target_mean": float(gate[mask].mean()),
                            "gate_background_mean": float(gate[~mask].mean()),
                        }
                    )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "p1_fixed_weight_fusion_official_detail.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(score_rows).to_csv(OUT / "p0_protocol_audit_score_means_by_frame.csv", index=False, encoding="utf-8-sig")
    summary = (
        detail.groupby(["method", "pfa_target", "w_residual"], dropna=False)
        .agg(pd_mean=("pd", "mean"), empirical_pfa_mean=("empirical_pfa", "mean"), n_items=("item_id", "nunique"))
        .reset_index()
    )
    summary.to_csv(OUT / "p1_fixed_weight_fusion_summary.csv", index=False, encoding="utf-8-sig")
    chosen = (
        summary[(summary["method"] == "fixed_weight_fusion") & (summary["pfa_target"] == 1e-5)]
        .sort_values(["pd_mean", "empirical_pfa_mean"], ascending=[False, True])
        .head(1)
    )
    w_best = float(chosen["w_residual"].iloc[0])
    compare = summary[
        ((summary["method"] != "fixed_weight_fusion") | (summary["w_residual"] == w_best))
        & (summary["pfa_target"].isin(PFAS))
    ].copy()
    compare["selected_global_w_by_pfa1e5"] = np.where(compare["method"].eq("fixed_weight_fusion"), w_best, np.nan)
    compare.to_csv(OUT / "p1_fixed_vs_adaptive_gate_summary.csv", index=False, encoding="utf-8-sig")
    ci = bootstrap_ci(detail, ["tpsscs_adaptive_gate", "raw", f"low_rank_residual_k{model.rank}", "fixed_weight_fusion"], w_best)
    ci.to_csv(OUT / "p1_bootstrap_ci_pfa1e5.csv", index=False, encoding="utf-8-sig")
    block = block_bootstrap_ci(detail, ["tpsscs_adaptive_gate", "raw", f"low_rank_residual_k{model.rank}", "fixed_weight_fusion"], w_best)
    block.to_csv(OUT / "p1_block_bootstrap_ci_pfa1e5.csv", index=False, encoding="utf-8-sig")
    return detail, compare, ci


def bootstrap_ci(detail: pd.DataFrame, methods: list[str], w_best: float, n_boot: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(20260722)
    df = detail[detail["pfa_target"].eq(1e-5)].copy()
    df = df[(df["method"].isin(methods)) & ((df["method"] != "fixed_weight_fusion") | df["w_residual"].eq(w_best))]
    piv = df.pivot_table(index="item_id", columns="method", values="pd", aggfunc="mean")
    rows = []
    ids = np.asarray(piv.index)
    for method in piv.columns:
        vals = piv[method].to_numpy(float)
        boots = np.array([np.nanmean(vals[rng.integers(0, len(vals), len(vals))]) for _ in range(n_boot)])
        rows.append({"method": method, "pfa": 1e-5, "mean_pd": float(np.nanmean(vals)), "ci95_low": float(np.quantile(boots, 0.025)), "ci95_high": float(np.quantile(boots, 0.975)), "n_items": int(len(ids)), "bootstrap_unit": "frame"})
    ref = "tpsscs_adaptive_gate"
    if ref in piv:
        for method in piv.columns:
            if method == ref:
                continue
            delta = (piv[ref] - piv[method]).to_numpy(float)
            boots = np.array([np.nanmean(delta[rng.integers(0, len(delta), len(delta))]) for _ in range(n_boot)])
            rows.append({"method": f"{ref}_minus_{method}", "pfa": 1e-5, "mean_pd": float(np.nanmean(delta)), "ci95_low": float(np.quantile(boots, 0.025)), "ci95_high": float(np.quantile(boots, 0.975)), "n_items": int(len(ids)), "bootstrap_unit": "paired_frame_delta"})
    return pd.DataFrame(rows)


def block_bootstrap_ci(detail: pd.DataFrame, methods: list[str], w_best: float, n_boot: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(20260722)
    df = detail[detail["pfa_target"].eq(1e-5)].copy()
    df = df[(df["method"].isin(methods)) & ((df["method"] != "fixed_weight_fusion") | df["w_residual"].eq(w_best))]
    item = df.pivot_table(index=["asset", "item_id"], columns="method", values="pd", aggfunc="mean").reset_index()
    blocks = list(item["asset"].unique())
    rows = []
    for method in [c for c in item.columns if c not in {"asset", "item_id"}]:
        block_means = item.groupby("asset")[method].mean().reindex(blocks).to_numpy(float)
        boots = np.array([np.nanmean(block_means[rng.integers(0, len(block_means), len(block_means))]) for _ in range(n_boot)])
        rows.append({"method": method, "pfa": 1e-5, "mean_pd": float(np.nanmean(item[method])), "ci95_low": float(np.quantile(boots, 0.025)), "ci95_high": float(np.quantile(boots, 0.975)), "n_blocks": int(len(blocks)), "bootstrap_unit": "asset_block"})
    return pd.DataFrame(rows)


def ipix_normalization_repair() -> pd.DataFrame:
    data_dir = ROOT / "data" / "downloads" / "ipix"
    files = sorted(data_dir.glob("*.cdf"))
    state = ROOT / "results" / "aistap_sample" / "tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt"
    model = load_trainable_model(state)
    model.eval()
    filenames = [p.name for p in files]
    all_items, _ = load_ipix_items(ROOT, filenames, model, window=1024, stride=1024, max_windows_per_file=24)
    rows = []
    for item in all_items:
        bg = item["background_mask"]
        scores = {
            "raw": item["raw_score"],
            "low_rank_residual": item["low_score"],
            "tpsscs_gate_score": item["gate_score"],
            "validated_residual_fusion": ipix_fusion_score(item, beta=0.25),
        }
        for name, score in scores.items():
            for row in summarize_ipix_score(score, item["target_mask"], bg, IPIX_PFAS, "conservative_topk_strict_gt"):
                row.update({"dataset": "IPIX_Dartmouth", "file": item["file"], "window_index": item["window_index"], "item_id": item["item_id"], "method": name})
                rows.append(row)
        for name, score in scores.items():
            mu = float(np.mean(score[bg]))
            sigma = float(np.std(score[bg]) + 1e-9)
            z = (score - mu) / sigma
            for row in summarize_ipix_score(z, item["target_mask"], bg, IPIX_PFAS, "conservative_topk_strict_gt"):
                row.update({"dataset": "IPIX_Dartmouth", "file": item["file"], "window_index": item["window_index"], "item_id": item["item_id"], "method": f"{name}_background_zscore"})
                rows.append(row)
            med = float(np.median(score[bg]))
            mad = float(np.median(np.abs(score[bg] - med)) + 1e-9)
            rz = (score - med) / (1.4826 * mad)
            for row in summarize_ipix_score(rz, item["target_mask"], bg, IPIX_PFAS, "conservative_topk_strict_gt"):
                row.update({"dataset": "IPIX_Dartmouth", "file": item["file"], "window_index": item["window_index"], "item_id": item["item_id"], "method": f"{name}_background_robust_zscore"})
                rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "p0_ipix_normalization_repair_detail.csv", index=False, encoding="utf-8-sig")
    summary = df.groupby(["method", "pfa_target"]).agg(pd_mean=("pd", "mean"), empirical_pfa_mean=("empirical_pfa", "mean"), n_windows=("item_id", "nunique")).reset_index()
    summary.to_csv(OUT / "p0_ipix_normalization_repair_summary.csv", index=False, encoding="utf-8-sig")
    return summary


def ssdd_tail_temperature() -> pd.DataFrame:
    dataset_root = ROOT / "data" / "downloads" / "ssdd" / "extracted" / "Official-SSDD-OPEN" / "BBox_RBox_PSeg_SSDD" / "coco_style"
    train_images, train_anns = load_coco(dataset_root / "annotations" / "train.json")
    test_images, test_anns = load_coco(dataset_root / "annotations" / "test.json")
    dev_ids, val_ids = split_train_ids(list(train_images))
    x_dev, y_dev, _ = sample_development(dataset_root, dev_ids, train_images, train_anns, 20260715, 800, 2400)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
    model.fit(x_dev, y_dev)
    test_pack = collect_split(dataset_root, "test", set(test_images), test_images, test_anns, model)
    rows = []
    for policy in ["raw", "lowrank", "gate"]:
        if policy == "lowrank":
            target_scores, bg_scores = test_pack["lowrank_t"], test_pack["lowrank_b"]
        else:
            target_scores, bg_scores = policy_scores(test_pack, policy)
        bg = np.asarray(bg_scores, float)
        centered = bg - bg.mean()
        std = bg.std() + 1e-12
        for pfa in SSDD_PFAS:
            threshold, _ = conservative_cfar_threshold(bg, pfa)
            rows.append(
                {
                    "policy": policy,
                    "temperature": 1.0,
                    "pfa": pfa,
                    "threshold": threshold,
                    "pd": float(np.mean(target_scores > threshold)),
                    "empirical_pfa": float(np.mean(bg > threshold)),
                    "bg_mean": float(bg.mean()),
                    "bg_std": float(bg.std()),
                    "bg_skew": float(np.mean((centered / std) ** 3)),
                    "bg_kurtosis": float(np.mean((centered / std) ** 4)),
                    "bg_q999": float(np.quantile(bg, 0.999)),
                    "bg_q9999": float(np.quantile(bg, 0.9999)),
                    "bg_max": float(bg.max()),
                    "threshold_minus_q9999": float(threshold - np.quantile(bg, 0.9999)),
                }
            )
    # Monotonic temperature scaling cannot change rank-based Pd/Pfa with per-score thresholds;
    # still record the audit explicitly for reviewer traceability.
    temp_rows = []
    gate_t, gate_b = policy_scores(test_pack, "gate")
    for temp in [0.5, 0.75, 1.0, 1.5, 2.0, 4.0]:
        scaled_t = gate_t / temp
        scaled_b = gate_b / temp
        for pfa in SSDD_PFAS:
            threshold, _ = conservative_cfar_threshold(scaled_b, pfa)
            temp_rows.append({"policy": "gate_temperature_scaled", "temperature": temp, "pfa": pfa, "threshold": threshold, "pd": float(np.mean(scaled_t > threshold)), "empirical_pfa": float(np.mean(scaled_b > threshold))})
    tail = pd.DataFrame(rows)
    temp_df = pd.DataFrame(temp_rows)
    tail.to_csv(OUT / "p1_ssdd_tail_moments.csv", index=False, encoding="utf-8-sig")
    temp_df.to_csv(OUT / "p1_ssdd_temperature_scaling.csv", index=False, encoding="utf-8-sig")
    return tail


def protocol_tables() -> None:
    protocol = pd.DataFrame(
        [
            {"dataset": "AISTAP-SIM full official", "split_or_asset": "simMed_test.mat, simWind_test.mat", "role": "held-out in-domain official evaluation", "labels_used_for_training": "No", "reviewer_risk_addressed": "same-distribution validation clarified; no test-label leakage claimed"},
            {"dataset": "AISTAP public sample", "split_or_asset": "simMed/simWind/simNoiseOnly preview", "role": "model fitting and mechanism diagnostics", "labels_used_for_training": "Yes, public sample only", "reviewer_risk_addressed": "gate is trained on simulation; cross-domain limitation stated"},
            {"dataset": "IPIX Dartmouth", "split_or_asset": "CDF windows", "role": "measured-domain stress test and unsupervised background calibration audit", "labels_used_for_training": "No target labels for normalization", "reviewer_risk_addressed": "calibration is reported as target-domain unsupervised adaptation, not pure zero-shot"},
            {"dataset": "SSDD", "split_or_asset": "official train/test", "role": "external SAR image robustness and low-PFA tail audit", "labels_used_for_training": "train split only for lightweight gate; test labels held out", "reviewer_risk_addressed": "low-PFA failure mode quantified"},
        ]
    )
    protocol.to_csv(OUT / "p0_protocol_audit_train_test_split.csv", index=False, encoding="utf-8-sig")
    hw = pd.DataFrame(
        [
            {"field": "os", "value": platform.platform()},
            {"field": "python", "value": sys.version.replace("\n", " ")},
            {"field": "processor", "value": platform.processor()},
            {"field": "torch", "value": torch.__version__},
            {"field": "cuda_available", "value": str(torch.cuda.is_available())},
            {"field": "cuda_device", "value": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "not available"},
        ]
    )
    hw.to_csv(OUT / "p2_runtime_hardware_context.csv", index=False, encoding="utf-8-sig")
    params = pd.DataFrame(
        [
            {"parameter": "AISTAP-SIM source", "value": "local full assets under data/downloads/aistap_sim/full", "evidence_status": "local file audit"},
            {"parameter": "evaluated official assets", "value": "simMed_test.mat; simWind_test.mat", "evidence_status": "present locally"},
            {"parameter": "radar waveform/platform parameters", "value": "AUTHOR_INPUT_NEEDED: verify against official AISTAP-SIM documentation before manuscript insertion", "evidence_status": "not inferred"},
        ]
    )
    params.to_csv(OUT / "p0_aistap_sim_parameter_table.csv", index=False, encoding="utf-8-sig")


def cfar_low_pfa() -> pd.DataFrame:
    src = ROOT / "results" / "aistap_full_asset" / "aistap_full_asset_classical_cfar_param_sweep_20260717.csv"
    df = pd.read_csv(src)
    low = df[df["pfa_target"].eq(1e-5)].copy()
    summary = low.groupby(["method", "method_family", "training_cells", "guard_cells", "os_percentile"], dropna=False).agg(pd_mean=("pd", "mean"), empirical_pfa_mean=("empirical_pfa", "mean"), n_items=("item_id", "nunique")).reset_index()
    summary.sort_values(["pd_mean", "empirical_pfa_mean"], ascending=[False, True]).to_csv(OUT / "p1_cfar_low_pfa_parameter_sweep.csv", index=False, encoding="utf-8-sig")
    return summary


def write_readme(payload: dict[str, Any]) -> None:
    lines = [
        "# Revision Modification 2 Experiment Pack",
        "",
        "Run from repository root:",
        "",
        "```powershell",
        "py scripts\\revision_mod2_experiments.py",
        "```",
        "",
        "Outputs are written to `results/revision_enhancement_20260722`.",
        "",
        "The pack addresses reviewer-style concerns with experiments wherever possible: fixed-weight fusion, IPIX background calibration, PFA=1e-5 bootstrap intervals, SSDD tail moments, CFAR low-PFA sweep, protocol audit, and hardware context.",
        "",
        "Important boundary: IPIX background normalization is unsupervised target-domain calibration, not pure zero-shot transfer.",
        "",
        "Summary:",
        json.dumps(payload, indent=2, ensure_ascii=False),
    ]
    (OUT / "README_revision_experiments.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    protocol_tables()
    _, fixed_compare, ci = aistap_fixed_fusion_and_bootstrap()
    ipix = ipix_normalization_repair()
    ssdd = ssdd_tail_temperature()
    cfar = cfar_low_pfa()
    payload = {
        "fixed_fusion_best_rows": fixed_compare[fixed_compare["pfa_target"].eq(1e-5)].sort_values("pd_mean", ascending=False).head(8).to_dict(orient="records"),
        "bootstrap_pfa1e5": ci.to_dict(orient="records"),
        "ipix_best_pfa1e5": ipix[ipix["pfa_target"].eq(1e-5)].sort_values("pd_mean", ascending=False).head(8).to_dict(orient="records"),
        "ssdd_tail_pfa1e5": ssdd[ssdd["pfa"].eq(1e-5)].to_dict(orient="records"),
        "cfar_best_pfa1e5": cfar.sort_values("pd_mean", ascending=False).head(8).to_dict(orient="records"),
    }
    (OUT / "revision_mod2_experiment_summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(payload)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
