from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import torch
from torch.utils.data import Dataset


def to_complex(arr: np.ndarray) -> np.ndarray:
    if arr.dtype.fields and {"real", "imag"} <= set(arr.dtype.fields):
        return arr["real"] + 1j * arr["imag"]
    return np.asarray(arr)


def _decode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.ndarray):
        if value.size == 1:
            return _decode_value(value.reshape(-1)[0])
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def list_sample_files(root: Path) -> list[Path]:
    sample_root = root / "data" / "downloads" / "aistap_sim" / "sampledata" / "sampledata"
    return sorted(sample_root.glob("*/*_sample.mat"))


@dataclass
class AISTAPItem:
    path: str
    subset: str
    image_index: int
    metadata: dict[str, Any]


class AISTAPSampleDataset(Dataset[AISTAPItem]):
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.files = list_sample_files(self.root)
        if not self.files:
            raise FileNotFoundError(f"No AISTAP sample files found under {self.root}")

        self.index: list[tuple[Path, int, dict[str, Any], str]] = []
        for path in self.files:
            with h5py.File(path, "r") as f:
                rd_img = f["rd_img"]
                refs = f["meta_per_image"][()]
                for i, ref in enumerate(refs.reshape(-1)):
                    meta = {}
                    grp = f[ref]
                    for key in grp.keys():
                        meta[key] = _decode_value(grp[key][()])
                    self.index.append((path, i, meta, path.parent.name))

        self._shape = None

    def __len__(self) -> int:
        return len(self.index)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        path, image_index, meta, subset = self.index[idx]
        with h5py.File(path, "r") as f:
            x = torch.from_numpy(to_complex(f["rd_img"][image_index])).to(torch.complex128)
            t = torch.from_numpy(to_complex(f["rd_targ_only"][image_index])).to(torch.complex128)
        return {
            "x": x,
            "target": t,
            "metadata": meta,
            "subset": subset,
            "path": str(path),
            "image_index": image_index,
        }

