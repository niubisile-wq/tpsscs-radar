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


def svd_energy_ratios(x: np.ndarray, topk: int = 10) -> dict[str, float]:
    s = np.linalg.svd(x, compute_uv=False)
    energy = s**2
    total = energy.sum()
    cum = np.cumsum(energy) / total
    out = {
        "rank1_energy": float(cum[min(0, len(cum) - 1)]),
        "rank5_energy": float(cum[min(4, len(cum) - 1)]),
        "rank10_energy": float(cum[min(9, len(cum) - 1)]),
        "s1": float(s[0]),
        "s2": float(s[1]) if len(s) > 1 else float("nan"),
        "s10": float(s[9]) if len(s) > 9 else float("nan"),
    }
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=str(Path.home() / "Desktop" / "TP-SSCS项目"),
        help="Repository root.",
    )
    args = parser.parse_args()

    root = Path(args.root)
    sample_root = root / "data" / "downloads" / "aistap_sim" / "sampledata" / "sampledata"
    result_dir = root / "results" / "aistap_sample"
    result_dir.mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    plots: list[tuple[str, np.ndarray]] = []

    for mat in sorted(sample_root.glob("*/*_sample.mat")):
        rd_img, rd_targ, metadata = read_sample(mat)
        subset = mat.parent.name
        # Use the first CPI and concatenate channels x range into rows.
        raw = rd_img[0].reshape(rd_img.shape[1] * rd_img.shape[2], rd_img.shape[3])
        targ = rd_targ[0].reshape(rd_targ.shape[1] * rd_targ.shape[2], rd_targ.shape[3])

        raw_stats = svd_energy_ratios(raw)
        targ_stats = svd_energy_ratios(targ)
        rows.append(
            {
                "dataset": subset,
                "file": str(mat),
                "raw_power": float(np.mean(np.abs(raw) ** 2)),
                "targ_power": float(np.mean(np.abs(targ) ** 2)),
                "raw_to_targ_power_ratio_db": float(
                    10.0 * np.log10((np.mean(np.abs(raw) ** 2) + 1e-12) / (np.mean(np.abs(targ) ** 2) + 1e-12))
                ),
                "raw_rank1_energy": raw_stats["rank1_energy"],
                "raw_rank5_energy": raw_stats["rank5_energy"],
                "raw_rank10_energy": raw_stats["rank10_energy"],
                "targ_rank1_energy": targ_stats["rank1_energy"],
                "targ_rank5_energy": targ_stats["rank5_energy"],
                "targ_rank10_energy": targ_stats["rank10_energy"],
                "midp_range": metadata.get("midp_range"),
                "midp_dop": metadata.get("midp_dop"),
            }
        )
        s = np.linalg.svd(raw, compute_uv=False)
        plots.append((subset, s))

    df = pd.DataFrame(rows)
    df.to_csv(result_dir / "aistap_sample_lowrank_stats.csv", index=False, encoding="utf-8-sig")
    (result_dir / "aistap_sample_lowrank_stats.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    for subset, s in plots:
        energy = np.cumsum(s**2) / np.sum(s**2)
        ax.plot(energy[:50], label=subset)
    ax.set_xlabel("Rank")
    ax.set_ylabel("Cumulative energy")
    ax.set_title("AISTAP sample low-rank decay on first CPI")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(result_dir / "aistap_sample_lowrank_decay.png", dpi=160)
    plt.close(fig)

    report = root / "logs" / "aistap_sample_lowrank_report.txt"
    lines = [
        "AISTAP sample low-rank audit",
        f"Root: {root}",
        f"Sample root: {sample_root}",
        f"Rows: {len(rows)}",
        "",
    ]
    for row in rows:
        lines.append(
            f"- {row['dataset']}: raw rank1={row['raw_rank1_energy']:.4f}, rank5={row['raw_rank5_energy']:.4f}, rank10={row['raw_rank10_energy']:.4f}"
        )
    report.write_text("\n".join(lines), encoding="utf-8-sig")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

