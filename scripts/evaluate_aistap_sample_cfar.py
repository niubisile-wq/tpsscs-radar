from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def to_complex(arr: np.ndarray) -> np.ndarray:
    if arr.dtype.fields and {"real", "imag"} <= set(arr.dtype.fields):
        return arr["real"] + 1j * arr["imag"]
    return np.asarray(arr)


def read_mat(path: Path) -> tuple[np.ndarray, list[dict[str, Any]]]:
    with h5py.File(path, "r") as f:
        rd_img = to_complex(f["rd_img"][()])
        refs = f["meta_per_image"][()]
        meta_list = []
        for ref in refs.reshape(-1):
            grp = f[ref]
            meta = {}
            for key in grp.keys():
                v = grp[key][()]
                if np.asarray(v).size == 1:
                    meta[key] = float(np.asarray(v).reshape(-1)[0])
                else:
                    meta[key] = np.asarray(v).tolist()
            meta_list.append(meta)
    return rd_img, meta_list


def low_rank_residual(x: np.ndarray, k: int) -> np.ndarray:
    u, s, vh = np.linalg.svd(x, full_matrices=False)
    approx = (u[:, :k] * s[:k]) @ vh[:k, :]
    return x - approx


def target_mask(meta: dict[str, Any], shape: tuple[int, int]) -> np.ndarray:
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


def summarize_scores(score: np.ndarray, mask: np.ndarray, pfa_levels: list[float]) -> list[dict[str, Any]]:
    bg = score[~mask]
    tgt = score[mask]
    rows = []
    for pfa in pfa_levels:
        thr = float(np.quantile(bg, 1.0 - pfa))
        pd = float((tgt >= thr).mean()) if tgt.size else float("nan")
        emp_pfa = float((bg >= thr).mean())
        rows.append(
            {
                "pfa_target": pfa,
                "threshold": thr,
                "pd": pd,
                "empirical_pfa": emp_pfa,
                "target_count": int(tgt.size),
                "bg_count": int(bg.size),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=str(Path.home() / "Desktop" / "TP-SSCS项目"),
        help="Repository root.",
    )
    parser.add_argument("--ks", default="1,3,5,10,20", help="Comma-separated low-rank orders.")
    parser.add_argument(
        "--pfas",
        default="1e-2,1e-3,1e-4",
        help="Comma-separated desired false alarm rates.",
    )
    args = parser.parse_args()

    root = Path(args.root)
    sample_root = root / "data" / "downloads" / "aistap_sim" / "sampledata" / "sampledata"
    out_dir = root / "results" / "aistap_sample"
    out_dir.mkdir(parents=True, exist_ok=True)

    ks = [int(x) for x in args.ks.split(",") if x.strip()]
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    rows = []

    for mat in sorted(sample_root.glob("*/*_sample.mat")):
        rd_img, meta_list = read_mat(mat)
        dataset = mat.parent.name
        for i, meta in enumerate(meta_list):
            raw = rd_img[i].reshape(rd_img.shape[1] * rd_img.shape[2], rd_img.shape[3])
            raw_score = np.sum(np.abs(raw).reshape(rd_img.shape[1], rd_img.shape[2], rd_img.shape[3]) ** 2, axis=0)
            mask = target_mask(meta, raw_score.shape)
            if not mask.any():
                continue

            for row in summarize_scores(raw_score, mask, pfas):
                rows.append(
                    {
                        "dataset": dataset,
                        "image_index": i,
                        "method": "raw",
                        "k": 0,
                        **row,
                    }
                )

            for k in ks:
                resid = low_rank_residual(raw, k)
                resid_score = np.sum(
                    np.abs(resid).reshape(rd_img.shape[1], rd_img.shape[2], rd_img.shape[3]) ** 2, axis=0
                )
                for row in summarize_scores(resid_score, mask, pfas):
                    rows.append(
                        {
                            "dataset": dataset,
                            "image_index": i,
                            "method": "low_rank_residual",
                            "k": k,
                            **row,
                        }
                    )

    df = pd.DataFrame(rows)
    tag = f"ks{args.ks.replace(',', '_')}_pfas{args.pfas.replace(',', '_')}"
    df.to_csv(out_dir / f"aistap_sample_cfar_{tag}.csv", index=False, encoding="utf-8-sig")
    (out_dir / f"aistap_sample_cfar_{tag}.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )

    # Aggregate plots
    fig, axes = plt.subplots(1, len(pfas), figsize=(5 * len(pfas), 4), sharey=True)
    if len(pfas) == 1:
        axes = [axes]
    for ax, pfa in zip(axes, pfas):
        sub = df[df["pfa_target"] == pfa].copy()
        for method, grp in sub.groupby("method"):
            if method == "raw":
                x = [0]
                y = [grp["pd"].mean()]
                ax.plot(x, y, marker="o", label=method)
            else:
                means = grp.groupby("k")["pd"].mean().reset_index()
                ax.plot(means["k"], means["pd"], marker="o", label=method)
        ax.set_title(f"Pd at Pfa={pfa:g}")
        ax.set_xlabel("k")
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("Pd")
    axes[-1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / f"aistap_sample_cfar_{tag}.png", dpi=160)
    plt.close(fig)

    report = root / "logs" / f"aistap_sample_cfar_{tag}.txt"
    lines = [
        "AISTAP sample CFAR audit",
        f"Root: {root}",
        f"ks: {args.ks}",
        f"pfas: {args.pfas}",
        "",
    ]
    if not df.empty:
        summary = (
            df.groupby(["method", "k", "pfa_target"])["pd"]
            .mean()
            .reset_index()
            .sort_values(["pfa_target", "method", "k"])
        )
        for _, row in summary.iterrows():
            lines.append(
                f"- method={row['method']} k={int(row['k'])} pfa={row['pfa_target']:g} pd={row['pd']:.4f}"
            )
    else:
        lines.append("No target masks matched; check coordinate mapping.")
    report.write_text("\n".join(lines), encoding="utf-8-sig")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

