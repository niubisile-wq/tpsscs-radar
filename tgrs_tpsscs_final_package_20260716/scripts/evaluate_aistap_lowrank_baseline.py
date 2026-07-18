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


def read_sample(path: Path) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    with h5py.File(path, "r") as f:
        rd_img = to_complex(f["rd_img"][()])
        rd_targ = to_complex(f["rd_targ_only"][()])
        metadata = {
            k: float(f["metadata"][k][()].reshape(-1)[0])
            if np.asarray(f["metadata"][k][()]).size == 1
            else np.asarray(f["metadata"][k][()]).tolist()
            for k in f["metadata"].keys()
        }
    return rd_img, rd_targ, metadata


def low_rank_residual(x: np.ndarray, k: int) -> np.ndarray:
    u, s, vh = np.linalg.svd(x, full_matrices=False)
    approx = (u[:, :k] * s[:k]) @ vh[:k, :]
    return x - approx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=str(Path.home() / "Desktop" / "TP-SSCS项目"),
        help="Repository root.",
    )
    parser.add_argument(
        "--ks",
        default="1,3,5,10,20",
        help="Comma-separated low-rank orders to evaluate.",
    )
    args = parser.parse_args()

    root = Path(args.root)
    sample_root = root / "data" / "downloads" / "aistap_sim" / "sampledata" / "sampledata"
    out_dir = root / "results" / "aistap_sample"
    out_dir.mkdir(parents=True, exist_ok=True)

    ks = [int(x.strip()) for x in args.ks.split(",") if x.strip()]
    rows = []
    for mat in sorted(sample_root.glob("*/*_sample.mat")):
        rd_img, rd_targ, metadata = read_sample(mat)
        subset = mat.parent.name
        raw = rd_img[0].reshape(rd_img.shape[1] * rd_img.shape[2], rd_img.shape[3])
        targ = rd_targ[0].reshape(rd_targ.shape[1] * rd_targ.shape[2], rd_targ.shape[3])

        raw_power = float(np.mean(np.abs(raw) ** 2))
        targ_power = float(np.mean(np.abs(targ) ** 2))

        for k in ks:
            residual = low_rank_residual(raw, k)
            targ_residual = low_rank_residual(targ, k)
            residual_power = float(np.mean(np.abs(residual) ** 2))
            targ_residual_power = float(np.mean(np.abs(targ_residual) ** 2))
            rows.append(
                {
                    "dataset": subset,
                    "k": k,
                    "raw_power": raw_power,
                    "residual_power": residual_power,
                    "clutter_attenuation_db": float(
                        10.0 * np.log10((raw_power + 1e-12) / (residual_power + 1e-12))
                    ),
                    "targ_power": targ_power,
                    "targ_residual_power": targ_residual_power,
                    "target_retention_ratio": float((targ_residual_power + 1e-12) / (targ_power + 1e-12)),
                    "target_loss_db": float(
                        10.0 * np.log10((targ_power + 1e-12) / (targ_residual_power + 1e-12))
                    ),
                    "midp_range": metadata.get("midp_range"),
                    "midp_dop": metadata.get("midp_dop"),
                }
            )

    df = pd.DataFrame(rows)
    tag = f"k{args.ks.replace(',', '_')}"
    df.to_csv(out_dir / f"aistap_lowrank_{tag}_baseline.csv", index=False, encoding="utf-8-sig")
    (out_dir / f"aistap_lowrank_{tag}_baseline.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    for subset, grp in df.groupby("dataset"):
        ax.plot(grp["k"], grp["clutter_attenuation_db"], marker="o", label=f"{subset} clutter")
        ax.plot(grp["k"], grp["target_loss_db"], marker="x", linestyle="--", label=f"{subset} target loss")
    ax.set_xlabel("Rank k")
    ax.set_ylabel("dB")
    ax.set_title("AISTAP sample low-rank baseline trade-off")
    ax.grid(True, alpha=0.3)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / f"aistap_lowrank_{tag}_baseline.png", dpi=160)
    plt.close(fig)

    report = root / "logs" / f"aistap_lowrank_{tag}_baseline_report.txt"
    lines = [
        "AISTAP low-rank baseline",
        f"Root: {root}",
        f"ks: {args.ks}",
        "",
    ]
    for row in rows:
        lines.append(
            f"- {row['dataset']}: clutter_attenuation_db={row['clutter_attenuation_db']:.3f}, target_loss_db={row['target_loss_db']:.3f}"
        )
    report.write_text("\n".join(lines), encoding="utf-8-sig")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

