from __future__ import annotations

import json
import sys
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
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
    target_mask,
    to_complex,
)
from evaluate_aistap_target_preservation_ablation import load_trainable_model  # noqa: E402
from revision_p2_lightweight_cnn_baseline import TinyCNN  # noqa: E402

OUT = ROOT / "results" / "revision_enhancement_20260722"


def detector_pd(raw: np.ndarray, residual: np.ndarray, gate_score: np.ndarray, mask: np.ndarray) -> tuple[float, float]:
    raw_thr, _ = conservative_cfar_threshold(raw[~mask], 1e-5)
    res_thr, _ = conservative_cfar_threshold(residual[~mask], 1e-5)
    gate_thr, _ = conservative_cfar_threshold(gate_score[~mask], 0.0)
    raw_pd = float((raw > raw_thr)[mask].mean())
    adaptive_pd = float(((residual > res_thr) | (gate_score > gate_thr))[mask].mean())
    return raw_pd, adaptive_pd


def find_failure_case(model: torch.nn.Module) -> dict[str, object]:
    assets = [
        ROOT / "data" / "downloads" / "aistap_sim" / "full" / "simMed_test.mat",
        ROOT / "data" / "downloads" / "aistap_sim" / "full" / "simWind_test.mat",
    ]
    best = None
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
                    out = model(torch.from_numpy(x_np).to(torch.complex128))
                    raw = score_map(x_np)
                    residual = score_map(out["residual"].detach().cpu().numpy())
                    gate_score = out["score"].detach().cpu().numpy()
                    gate_weight = out["gate"].detach().cpu().numpy()
                    raw_pd, adaptive_pd = detector_pd(raw, residual, gate_score, mask)
                    gap = raw_pd - adaptive_pd
                    if best is None or gap > best["gap"]:
                        best = {
                            "asset": asset,
                            "image_index": idx,
                            "raw": raw,
                            "residual": residual,
                            "gate_score": gate_score,
                            "gate_weight": gate_weight,
                            "mask": mask,
                            "raw_pd": raw_pd,
                            "adaptive_pd": adaptive_pd,
                            "gap": gap,
                        }
    if best is None:
        raise RuntimeError("No target-bearing frame found")
    return best


def save_failure_heatmap(case: dict[str, object]) -> Path:
    raw = np.log1p(case["raw"])
    residual = np.log1p(case["residual"])
    gate_score = np.log1p(case["gate_score"])
    gate_weight = case["gate_weight"]
    mask = case["mask"]
    coords = np.argwhere(mask)
    fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.2), constrained_layout=True)
    panels = [
        ("raw score", raw),
        ("residual score", residual),
        ("gate raw weight", gate_weight),
        ("adaptive score", gate_score),
    ]
    for ax, (title, arr) in zip(axes, panels):
        im = ax.imshow(arr, aspect="auto", cmap="viridis")
        ax.scatter(coords[:, 1], coords[:, 0], s=22, facecolors="none", edgecolors="red", linewidths=0.9)
        ax.set_title(title, fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    fig.suptitle(
        f"Failure-oriented audit: {Path(case['asset']).name}#{case['image_index']} raw Pd={case['raw_pd']:.3f}, adaptive Pd={case['adaptive_pd']:.3f}",
        fontsize=10,
    )
    out = OUT / "p2_failure_case_heatmap_aistap_official_pfa1e5.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out


def cnn_protocol() -> Path:
    model = TinyCNN(width=8)
    params = sum(p.numel() for p in model.parameters())
    train_log = json.loads((ROOT / "results" / "revision_enhancement_20260721" / "p2_tiny_cnn_training_log.json").read_text(encoding="utf-8"))
    summary = pd.read_csv(ROOT / "results" / "revision_enhancement_20260721" / "p2_tiny_cnn_official_summary.csv")
    rows = [
        {"field": "architecture", "value": "Conv2d(2,8,3,pad=1)-ReLU-Conv2d(8,8,3,pad=1)-ReLU-Conv2d(8,1,1)"},
        {"field": "parameter_count", "value": str(params)},
        {"field": "input_channels", "value": "z-scored log raw score and z-scored log rank-30 residual score"},
        {"field": "training_source", "value": "AISTAP public sample target-bearing items only"},
        {"field": "training_steps", "value": "150"},
        {"field": "optimizer", "value": "Adam, lr=0.01"},
        {"field": "loss", "value": "pixelwise BCEWithLogitsLoss with clipped positive class weight <=200"},
        {"field": "seed", "value": "20260721"},
        {"field": "training_log", "value": json.dumps(train_log, ensure_ascii=False)},
        {"field": "official_pd_at_1e-5", "value": str(float(summary.loc[summary["pfa_target"].eq(1e-5), "pd_mean"].iloc[0]))},
        {"field": "official_pd_at_1e-2", "value": str(float(summary.loc[summary["pfa_target"].eq(1e-2), "pd_mean"].iloc[0]))},
        {"field": "interpretation", "value": "lightweight sanity baseline; not claimed as strongest possible CNN/SAR detector"},
    ]
    out = OUT / "p2_cnn_architecture_protocol.csv"
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    state = ROOT / "results" / "aistap_sample" / "tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt"
    model = load_trainable_model(state)
    model.eval()
    case = find_failure_case(model)
    heatmap = save_failure_heatmap(case)
    case_meta = {
        "asset": Path(case["asset"]).name,
        "image_index": int(case["image_index"]),
        "raw_pd_at_1e-5": float(case["raw_pd"]),
        "adaptive_pd_at_1e-5": float(case["adaptive_pd"]),
        "raw_minus_adaptive_pd": float(case["gap"]),
        "heatmap": str(heatmap),
    }
    (OUT / "p2_failure_case_heatmap_meta.json").write_text(json.dumps(case_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    protocol = cnn_protocol()
    print(heatmap)
    print(protocol)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
