from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
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


def decode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.ndarray):
        if value.dtype == object:
            return [decode_value(v) for v in value.ravel().tolist()]
        if value.dtype.fields and {"real", "imag"} <= set(value.dtype.fields):
            comp = to_complex(value)
            if comp.size == 1:
                return complex(comp.reshape(-1)[0])
            return comp.tolist()
        if value.size == 1:
            return decode_value(value.reshape(-1)[0])
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def read_group_dict(group: h5py.Group) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in group.keys():
        out[key] = decode_value(group[key][()])
    return out


@dataclass
class FileSummary:
    dataset: str
    path: str
    rd_img_shape: list[int]
    rd_targ_only_shape: list[int]
    num_cpi: int
    num_channels: int
    num_range: int
    num_doppler: int
    metadata: dict[str, Any]
    images: list[dict[str, Any]]


def summarize_mat(path: Path) -> tuple[FileSummary, np.ndarray, np.ndarray]:
    with h5py.File(path, "r") as f:
        rd_img = to_complex(f["rd_img"][()])
        rd_targ = to_complex(f["rd_targ_only"][()])
        metadata = read_group_dict(f["metadata"])

        meta_per_image = []
        refs = f["meta_per_image"][()]
        for ref in refs.reshape(-1):
            grp = f[ref]
            meta_per_image.append(read_group_dict(grp))

    rd_shape = list(map(int, rd_img.shape))
    file_summary = FileSummary(
        dataset=path.parent.name,
        path=str(path),
        rd_img_shape=rd_shape,
        rd_targ_only_shape=list(map(int, rd_targ.shape)),
        num_cpi=int(rd_shape[0]),
        num_channels=int(rd_shape[1]),
        num_range=int(rd_shape[2]),
        num_doppler=int(rd_shape[3]),
        metadata=metadata,
        images=meta_per_image,
    )
    return file_summary, rd_img, rd_targ


def log_magnitude(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    return np.log10(np.abs(x) + eps)


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
    out_dir = root / "data" / "processed" / "aistap_sample"
    out_dir.mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(parents=True, exist_ok=True)

    mat_files = sorted(sample_root.glob("*/*_sample.mat"))
    if not mat_files:
        raise FileNotFoundError(f"No sample .mat files found under {sample_root}")

    summaries: list[FileSummary] = []
    overview_rows: list[dict[str, Any]] = []
    preview_images: list[np.ndarray] = []
    preview_targets: list[np.ndarray] = []
    preview_labels: list[str] = []

    for mat in mat_files:
        summary, rd_img, rd_targ = summarize_mat(mat)
        summaries.append(summary)
        overview_rows.append(
            {
                "dataset": summary.dataset,
                "path": summary.path,
                "cpi": summary.num_cpi,
                "channels": summary.num_channels,
                "range": summary.num_range,
                "doppler": summary.num_doppler,
                "midp_range": summary.metadata.get("midp_range"),
                "midp_dop": summary.metadata.get("midp_dop"),
                "midp_ch": summary.metadata.get("midp_ch"),
                "num_antenna_channels": summary.metadata.get("num_antenna_channels"),
            }
        )
        preview_images.append(log_magnitude(rd_img[0, 0]))
        preview_targets.append(log_magnitude(rd_targ[0, 0]))
        preview_labels.append(summary.dataset)

        np.savez_compressed(
            out_dir / f"{summary.dataset}_preview.npz",
            rd_img=rd_img[0],
            rd_targ_only=rd_targ[0],
            metadata=json.dumps(summary.metadata, ensure_ascii=False),
            images=json.dumps(summary.images, ensure_ascii=False),
        )

    df = pd.DataFrame(overview_rows)
    df.to_csv(
        root / "data" / "manifests" / "aistap_sample_inventory.csv",
        index=False,
        encoding="utf-8-sig",
    )
    (root / "data" / "manifests" / "aistap_sample_inventory.json").write_text(
        json.dumps([asdict(s) for s in summaries], ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )

    fig, axes = plt.subplots(len(preview_images), 2, figsize=(10, 3.5 * len(preview_images)))
    if len(preview_images) == 1:
        axes = np.array([axes])
    for row, (img, tgt, label) in enumerate(zip(preview_images, preview_targets, preview_labels)):
        ax1 = axes[row, 0]
        ax2 = axes[row, 1]
        im1 = ax1.imshow(img, aspect="auto", origin="lower", cmap="magma")
        ax1.set_title(f"{label} rd_img[0,0] log10|x|")
        ax1.set_xlabel("Doppler bin")
        ax1.set_ylabel("Range bin")
        plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
        im2 = ax2.imshow(tgt, aspect="auto", origin="lower", cmap="viridis")
        ax2.set_title(f"{label} rd_targ_only[0,0] log10|x|")
        ax2.set_xlabel("Doppler bin")
        ax2.set_ylabel("Range bin")
        plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(root / "logs" / "aistap_sample_preview.png", dpi=160)
    plt.close(fig)

    report_lines = [
        "AISTAP sample inventory",
        f"Root: {root}",
        f"Sample root: {sample_root}",
        f"Files: {len(mat_files)}",
        "",
        "Rows:",
    ]
    for row in overview_rows:
        report_lines.append(
            f"- {row['dataset']} | cpi={row['cpi']} | channels={row['channels']} | range={row['range']} | doppler={row['doppler']}"
        )
    (root / "logs" / "aistap_sample_inventory_report.txt").write_text(
        "\n".join(report_lines), encoding="utf-8-sig"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

