from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tpsscs import AISTAPSampleDataset, TPSSCSPrototype


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=str(Path.home() / "Desktop" / "TP-SSCS项目"),
        help="Repository root.",
    )
    parser.add_argument("--rank", type=int, default=5)
    args = parser.parse_args()

    root = Path(args.root)
    ds = AISTAPSampleDataset(root)
    item = ds[0]
    x = item["x"]

    model = TPSSCSPrototype(rank=args.rank)
    out = model(x)

    result_dir = root / "results" / "tpsscs_smoke"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        result_dir / "smoke_outputs.npz",
        suppressed=out["suppressed"].detach().cpu().numpy(),
        residual=out["residual"].detach().cpu().numpy(),
        clutter=out["clutter"].detach().cpu().numpy(),
        score=out["score"].detach().cpu().numpy(),
    )

    report = {
        "subset": item["subset"],
        "path": item["path"],
        "image_index": item["image_index"],
        "input_shape": list(x.shape),
        "suppressed_shape": list(out["suppressed"].shape),
        "score_shape": list(out["score"].shape),
        "input_power": float(torch.mean(torch.abs(x) ** 2).item()),
        "suppressed_power": float(torch.mean(torch.abs(out["suppressed"]) ** 2).item()),
        "residual_power": float(torch.mean(torch.abs(out["residual"]) ** 2).item()),
        "clutter_power": float(torch.mean(torch.abs(out["clutter"]) ** 2).item()),
        "rank": args.rank,
    }
    (log_dir / "tpsscs_smoke_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )
    (log_dir / "tpsscs_smoke_report.txt").write_text(
        "\n".join([f"{k}: {v}" for k, v in report.items()]), encoding="utf-8-sig"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

