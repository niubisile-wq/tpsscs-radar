from __future__ import annotations

import json
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr


ROOT = Path(__file__).resolve().parents[1]
MRMS_DIR = Path(r"C:\mrms1")
FILES = [
    MRMS_DIR / "MRMS_ReflectivityAtLowestAltitude_00.50_20201014-000025.grib2",
    MRMS_DIR / "MRMS_ReflectivityAtLowestAltitude_00.50_20201014-000227.grib2",
    MRMS_DIR / "MRMS_ReflectivityAtLowestAltitude_00.50_20201014-000438.grib2",
]
THRESHOLDS = [20.0, 30.0, 40.0, 50.0]


def safe_div(num: float, den: float) -> float:
    return float(num / den) if den else 0.0


def load_field(path: Path) -> tuple[dict[str, str], np.ndarray]:
    ds = xr.open_dataset(path, engine="cfgrib", backend_kwargs={"indexpath": ""})
    var = list(ds.data_vars)[0]
    arr = ds[var].values.astype(np.float32)
    arr = np.where(arr <= -900, np.nan, arr)
    meta = {
        "file": path.name,
        "valid_time": str(ds.coords.get("valid_time").values) if "valid_time" in ds.coords else "",
        "shape": str(tuple(arr.shape)),
        "min": f"{float(np.nanmin(arr)):.1f}",
        "max": f"{float(np.nanmax(arr)):.1f}",
    }
    return meta, arr


def downsample(arr: np.ndarray, size: tuple[int, int] = (700, 350)) -> np.ndarray:
    # OpenCV expects width, height.
    return cv2.resize(np.nan_to_num(arr, nan=-99.0), size, interpolation=cv2.INTER_AREA)


def farneback_forecast(prev: np.ndarray, cur: np.ndarray, target_shape: tuple[int, int]) -> np.ndarray:
    # Use the motion estimated from prev->cur to advect the latest frame.
    prev_u8 = cv2.normalize(prev, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    cur_u8 = cv2.normalize(cur, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    flow = cv2.calcOpticalFlowFarneback(prev_u8, cur_u8, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    h, w = target_shape
    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (grid_x + flow[..., 0]).astype(np.float32)
    map_y = (grid_y + flow[..., 1]).astype(np.float32)
    return cv2.remap(cur, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=-99.0)


def scores(pred: np.ndarray, truth: np.ndarray, thr: float) -> dict[str, float]:
    mask = np.isfinite(pred) & np.isfinite(truth)
    pred_bin = (pred >= thr) & mask
    truth_bin = (truth >= thr) & mask
    hits = float(np.sum(pred_bin & truth_bin))
    misses = float(np.sum(~pred_bin & truth_bin))
    false_alarms = float(np.sum(pred_bin & ~truth_bin))
    csi = safe_div(hits, hits + misses + false_alarms)
    pod = safe_div(hits, hits + misses)
    far = safe_div(false_alarms, hits + false_alarms)
    return {
        "hits": hits,
        "misses": misses,
        "false_alarms": false_alarms,
        "CSI": csi,
        "POD": pod,
        "FAR": far,
    }


def pair_metrics(pred: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(pred) & np.isfinite(truth)
    diff = pred[mask] - truth[mask]
    return {
        "MAE": float(np.mean(np.abs(diff))),
        "RMSE": float(np.sqrt(np.mean(diff ** 2))),
    }


def main() -> int:
    metas = []
    fields = []
    for p in FILES:
        meta, arr = load_field(p)
        metas.append(meta)
        fields.append(downsample(arr))

    report = {"metadata": metas, "pairs": []}
    rows = []

    # Use the first interval to estimate flow and forecast the third frame.
    prev = fields[0]
    cur = fields[1]
    truth = fields[2]
    flow_pred = farneback_forecast(prev, cur, truth.shape)
    persist_pred = cur

    pair = {
        "pair": f"{FILES[0].name} + {FILES[1].name} -> {FILES[2].name}",
        "flow": pair_metrics(flow_pred, truth),
        "persistence": pair_metrics(persist_pred, truth),
        "thresholds": {},
    }
    for thr in THRESHOLDS:
        pair["thresholds"][str(thr)] = {
            "flow": scores(flow_pred, truth, thr),
            "persistence": scores(persist_pred, truth, thr),
        }
    report["pairs"].append(pair)
    rows.append(
        {
            "pair": pair["pair"],
            "flow_mae": pair["flow"]["MAE"],
            "persist_mae": pair["persistence"]["MAE"],
            "flow_rmse": pair["flow"]["RMSE"],
            "persist_rmse": pair["persistence"]["RMSE"],
            "flow_csi20": pair["thresholds"]["20.0"]["flow"]["CSI"],
            "persist_csi20": pair["thresholds"]["20.0"]["persistence"]["CSI"],
            "flow_csi30": pair["thresholds"]["30.0"]["flow"]["CSI"],
            "persist_csi30": pair["thresholds"]["30.0"]["persistence"]["CSI"],
        }
    )

    out_dir = ROOT / "results" / "mrms_external"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = ROOT / "logs"
    fig_dir = ROOT / "figures" / "main"
    fig_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(rows).to_csv(out_dir / "mrms_farneback_forecast_summary.csv", index=False, encoding="utf-8-sig")
    (out_dir / "mrms_farneback_forecast_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8-sig")

    lines = ["# MRMS Farneback Forecast", ""]
    for meta in metas:
        lines.append(
            f"- file={meta['file']} valid_time={meta['valid_time']} shape={meta['shape']} min={meta['min']} max={meta['max']}"
        )
    lines.append("")
    for row in rows:
        lines.append(
            f"- {row['pair']}: flow_mae={row['flow_mae']:.4f} persist_mae={row['persist_mae']:.4f} "
            f"flow_rmse={row['flow_rmse']:.4f} persist_rmse={row['persist_rmse']:.4f} "
            f"flow_csi20={row['flow_csi20']:.4f} persist_csi20={row['persist_csi20']:.4f} "
            f"flow_csi30={row['flow_csi30']:.4f} persist_csi30={row['persist_csi30']:.4f}"
        )
    (log_dir / "mrms_farneback_forecast_20260713.md").write_text("\n".join(lines), encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(["flow", "persistence"], [rows[0]["flow_mae"], rows[0]["persist_mae"]], color=["#2a9d8f", "#e76f51"])
    ax.set_ylabel("MAE")
    ax.set_title("MRMS F0+F1 -> F2 MAE on 700x350 downsample")
    fig.tight_layout()
    fig.savefig(fig_dir / "figure9_mrms_farneback_forecast.svg", dpi=160)
    plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
