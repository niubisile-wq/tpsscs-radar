from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for p in [SRC, SCRIPTS]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from revision_p0_gate_and_ipix_shift import score_map, target_mask  # noqa: E402
from tpsscs import AISTAPSampleDataset  # noqa: E402


OUT = ROOT / "results" / "revision_enhancement_20260722"


def lowrank_projection_stats(x: np.ndarray, rank: int = 30) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return raw score, residual score, and projection-energy fraction per cell.

    The low-rank basis is estimated from the same C*D by R matrix used by the
    residual comparator. For each cell vector over channels, we measure how much
    energy lies in the rank-k left subspace. This is a direct empirical proxy for
    how much a target-like cell is representable by the estimated clutter subspace.
    """
    mat = x.reshape(x.shape[0] * x.shape[1], x.shape[2])
    u, s, vh = np.linalg.svd(mat, full_matrices=False)
    k = min(rank, s.shape[0])
    basis = u[:, :k]
    approx = (basis * s[:k]) @ vh[:k, :]
    residual = (mat - approx).reshape(x.shape)
    approx_cube = approx.reshape(x.shape)
    raw_energy = score_map(x)
    residual_energy = score_map(residual)
    projection_energy = score_map(approx_cube)
    projection_fraction = projection_energy / np.maximum(raw_energy, 1e-12)
    return raw_energy, residual_energy, projection_fraction


def main() -> int:
    ds = AISTAPSampleDataset(ROOT)
    rows = []
    for item in ds:
        x = item["x"].detach().cpu().numpy()
        raw, residual, frac = lowrank_projection_stats(x, rank=30)
        mask = target_mask(item["metadata"], raw.shape)
        if not mask.any():
            continue
        absorption = raw - residual
        rel_absorption = absorption / np.maximum(raw, 1e-12)
        for d, r in np.argwhere(mask):
            rows.append(
                {
                    "subset": item["subset"],
                    "image_index": int(item["image_index"]),
                    "doppler_index": int(d),
                    "range_index": int(r),
                    "raw_score": float(raw[d, r]),
                    "residual_score": float(residual[d, r]),
                    "residual_absorption": float(absorption[d, r]),
                    "relative_absorption": float(rel_absorption[d, r]),
                    "subspace_projection_fraction": float(frac[d, r]),
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No target cells found")
    df["projection_bin"] = pd.qcut(
        df["subspace_projection_fraction"].rank(method="first"),
        4,
        labels=["Q1_low", "Q2", "Q3", "Q4_high"],
    ).astype(str)
    summary = (
        df.groupby("projection_bin")
        .agg(
            n=("subspace_projection_fraction", "size"),
            projection_fraction_mean=("subspace_projection_fraction", "mean"),
            relative_absorption_mean=("relative_absorption", "mean"),
            residual_absorption_mean=("residual_absorption", "mean"),
            raw_score_mean=("raw_score", "mean"),
            residual_score_mean=("residual_score", "mean"),
        )
        .reset_index()
    )
    pearson = float(df[["subspace_projection_fraction", "relative_absorption"]].corr(method="pearson").iloc[0, 1])
    spearman = float(df[["subspace_projection_fraction", "relative_absorption"]].corr(method="spearman").iloc[0, 1])
    payload = {
        "rank": 30,
        "n_target_cells": int(len(df)),
        "pearson_projection_vs_relative_absorption": pearson,
        "spearman_projection_vs_relative_absorption": spearman,
        "summary": summary.to_dict(orient="records"),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "p0_subspace_projection_absorption_detail.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "p0_subspace_projection_absorption_summary.csv", index=False, encoding="utf-8-sig")
    (OUT / "p0_subspace_projection_absorption.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
