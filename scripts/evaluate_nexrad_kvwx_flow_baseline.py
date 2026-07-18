from __future__ import annotations

import io
import json
from pathlib import Path

import boto3
import botocore
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from botocore.client import Config
from metpy.io import Level2File


ROOT = Path(__file__).resolve().parents[1]
BUCKET_NAME = "unidata-nexrad-level2"
PREFIX = "2019/06/26/KVWX/"
RUN_NAME = "nexrad_kvwx"
KEYS = [
    "2019/06/26/KVWX/KVWX20190626_000255_V06",
    "2019/06/26/KVWX/KVWX20190626_001235_V06",
    "2019/06/26/KVWX/KVWX20190626_002215_V06",
    "2019/06/26/KVWX/KVWX20190626_003155_V06",
    "2019/06/26/KVWX/KVWX20190626_004135_V06",
    "2019/06/26/KVWX/KVWX20190626_005114_V06",
    "2019/06/26/KVWX/KVWX20190626_010054_V06",
    "2019/06/26/KVWX/KVWX20190626_011034_V06",
]
THRESHOLDS = [10.0, 20.0, 30.0]


def safe_div(num: float, den: float) -> float:
    return float(num / den) if den else 0.0


def load_reflectivity(key: str) -> tuple[str, np.ndarray]:
    s3 = boto3.resource("s3", config=Config(signature_version=botocore.UNSIGNED, user_agent_extra="Resource"))
    body = s3.Bucket(BUCKET_NAME).Object(key).get()["Body"].read()
    lvl2 = Level2File(io.BytesIO(body))
    sweep = lvl2.sweeps[0]
    ref = np.array([ray[4][b"REF"][1] for ray in sweep], dtype=np.float32)
    ref[ref < -90] = np.nan
    return str(lvl2.dt), ref


def farneback_predict(prev: np.ndarray, cur: np.ndarray) -> np.ndarray:
    prev_u8 = cv2.normalize(np.nan_to_num(prev, nan=np.nanmean(prev)), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    cur_u8 = cv2.normalize(np.nan_to_num(cur, nan=np.nanmean(cur)), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    flow = cv2.calcOpticalFlowFarneback(prev_u8, cur_u8, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    h, w = cur.shape
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    return cv2.remap(
        cur,
        (x + flow[..., 0]).astype(np.float32),
        (y + flow[..., 1]).astype(np.float32),
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=np.nan,
    )


def metrics(pred: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(pred) & np.isfinite(truth)
    diff = pred[mask] - truth[mask]
    out = {
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff ** 2))),
    }
    for thr in THRESHOLDS:
        pred_bin = pred[mask] >= thr
        truth_bin = truth[mask] >= thr
        tp = float(np.logical_and(pred_bin, truth_bin).sum())
        fp = float(np.logical_and(pred_bin, ~truth_bin).sum())
        fn = float(np.logical_and(~pred_bin, truth_bin).sum())
        out[f"csi_{int(thr)}"] = safe_div(tp, tp + fp + fn)
    return out


def main() -> int:
    stamps = []
    frames = []
    for key in KEYS:
        stamp, ref = load_reflectivity(key)
        stamps.append(stamp)
        frames.append(ref)

    rows = []
    triplet_report = []
    for idx in range(len(frames) - 2):
        prev, cur, truth = frames[idx], frames[idx + 1], frames[idx + 2]
        flow_pred = farneback_predict(prev, cur)
        persist_pred = cur
        flow_m = metrics(flow_pred, truth)
        persist_m = metrics(persist_pred, truth)
        row = {
            "triplet": f"{KEYS[idx]} + {KEYS[idx + 1]} -> {KEYS[idx + 2]}",
            "prev_time": stamps[idx],
            "cur_time": stamps[idx + 1],
            "truth_time": stamps[idx + 2],
            "flow_mae": flow_m["mae"],
            "persist_mae": persist_m["mae"],
            "flow_rmse": flow_m["rmse"],
            "persist_rmse": persist_m["rmse"],
            "flow_csi10": flow_m["csi_10"],
            "persist_csi10": persist_m["csi_10"],
            "flow_csi20": flow_m["csi_20"],
            "persist_csi20": persist_m["csi_20"],
            "flow_csi30": flow_m["csi_30"],
            "persist_csi30": persist_m["csi_30"],
        }
        rows.append(row)
        triplet_report.append(
            {
                "triplet": row["triplet"],
                "flow": flow_m,
                "persistence": persist_m,
            }
        )

    summary = {
        "bucket": BUCKET_NAME,
        "prefix": PREFIX,
        "keys": KEYS,
        "n_triplets": len(rows),
        "mean": {
            "flow_mae": float(np.mean([r["flow_mae"] for r in rows])),
            "persist_mae": float(np.mean([r["persist_mae"] for r in rows])),
            "flow_rmse": float(np.mean([r["flow_rmse"] for r in rows])),
            "persist_rmse": float(np.mean([r["persist_rmse"] for r in rows])),
            "flow_csi10": float(np.mean([r["flow_csi10"] for r in rows])),
            "persist_csi10": float(np.mean([r["persist_csi10"] for r in rows])),
            "flow_csi20": float(np.mean([r["flow_csi20"] for r in rows])),
            "persist_csi20": float(np.mean([r["persist_csi20"] for r in rows])),
            "flow_csi30": float(np.mean([r["flow_csi30"] for r in rows])),
            "persist_csi30": float(np.mean([r["persist_csi30"] for r in rows])),
        },
        "triplets": triplet_report,
    }

    out_dir = ROOT / "results" / "nexrad_external"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = ROOT / "figures" / "main"
    fig_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(rows).to_csv(out_dir / f"{RUN_NAME}_flow_baseline_summary.csv", index=False, encoding="utf-8-sig")
    (out_dir / f"{RUN_NAME}_flow_baseline_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8-sig")

    lines = [
        f"# NEXRAD {RUN_NAME.upper()} Farneback Baseline",
        "",
        f"- bucket: {BUCKET_NAME}",
        f"- prefix: {PREFIX}",
        f"- n_triplets: {len(rows)}",
        "",
    ]
    for row in rows:
        lines.append(
            f"- {row['triplet']}: flow_mae={row['flow_mae']:.4f} persist_mae={row['persist_mae']:.4f} "
            f"flow_rmse={row['flow_rmse']:.4f} persist_rmse={row['persist_rmse']:.4f} "
            f"flow_csi20={row['flow_csi20']:.4f} persist_csi20={row['persist_csi20']:.4f}"
        )
    lines.append("")
    lines.append("## Mean")
    for k, v in summary["mean"].items():
        lines.append(f"- {k}: {v:.4f}")

    (log_dir / f"{RUN_NAME}_farneback_baseline_20260713.md").write_text("\n".join(lines), encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7, 4))
    labels = ["MAE", "RMSE"]
    flow_vals = [summary["mean"]["flow_mae"], summary["mean"]["flow_rmse"]]
    persist_vals = [summary["mean"]["persist_mae"], summary["mean"]["persist_rmse"]]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, flow_vals, width=0.36, label="Farneback", color="#2a9d8f")
    ax.bar(x + 0.18, persist_vals, width=0.36, label="Persistence", color="#e76f51")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("dBZ")
    ax.set_title(f"NEXRAD {RUN_NAME.upper()} mean error on {len(rows)} held-out triplets")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / f"figure10_{RUN_NAME}_farneback_baseline.svg", dpi=160)
    plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
