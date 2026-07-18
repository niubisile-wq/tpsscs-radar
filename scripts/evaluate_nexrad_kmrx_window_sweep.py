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
PREFIX = "2019/05/20/KMRX/"
RUN_NAME = "nexrad_kmrx_window_sweep"
WINDOW_STARTS = [220, 230, 240]
WINDOW_SIZE = 6
THRESHOLDS = [10.0, 20.0, 30.0]


def safe_div(num: float, den: float) -> float:
    return float(num / den) if den else 0.0


def load_reflectivity(s3: boto3.client, key: str) -> np.ndarray:
    body = s3.get_object(Bucket=BUCKET_NAME, Key=key)["Body"].read()
    lvl2 = Level2File(io.BytesIO(body))
    sweep = lvl2.sweeps[0]
    ref = np.array([ray[4][b"REF"][1] for ray in sweep], dtype=np.float32)
    ref[ref < -90] = np.nan
    return ref


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


def summarize_rows(rows: list[dict[str, float]]) -> dict[str, float]:
    return {
        "mean_flow_mae": float(np.mean([r["flow_mae"] for r in rows])),
        "mean_persist_mae": float(np.mean([r["persist_mae"] for r in rows])),
        "mean_flow_rmse": float(np.mean([r["flow_rmse"] for r in rows])),
        "mean_persist_rmse": float(np.mean([r["persist_rmse"] for r in rows])),
        "mean_flow_csi10": float(np.mean([r["flow_csi10"] for r in rows])),
        "mean_persist_csi10": float(np.mean([r["persist_csi10"] for r in rows])),
        "mean_flow_csi20": float(np.mean([r["flow_csi20"] for r in rows])),
        "mean_persist_csi20": float(np.mean([r["persist_csi20"] for r in rows])),
        "mean_flow_csi30": float(np.mean([r["flow_csi30"] for r in rows])),
        "mean_persist_csi30": float(np.mean([r["persist_csi30"] for r in rows])),
    }


def main() -> int:
    s3 = boto3.client("s3", config=Config(signature_version=botocore.UNSIGNED, user_agent_extra="Resource"))
    resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
    keys = sorted([x["Key"] for x in resp.get("Contents", []) if x["Key"].endswith("_V06")])

    cache: dict[str, np.ndarray] = {}

    def cached_load(key: str) -> np.ndarray:
        if key not in cache:
            cache[key] = load_reflectivity(s3, key)
        return cache[key]

    rows = []
    triplet_rows = []
    for start in WINDOW_STARTS:
        window_keys = keys[start : start + WINDOW_SIZE]
        if len(window_keys) < WINDOW_SIZE:
            continue
        frames = [cached_load(key) for key in window_keys]
        triplet_metrics = []
        triplet_report = []
        for idx in range(WINDOW_SIZE - 2):
            prev, cur, truth = frames[idx], frames[idx + 1], frames[idx + 2]
            flow_m = metrics(farneback_predict(prev, cur), truth)
            persist_m = metrics(cur, truth)
            triplet_metrics.append(
                {
                    "triplet_index": idx,
                    "prev_key": window_keys[idx],
                    "cur_key": window_keys[idx + 1],
                    "truth_key": window_keys[idx + 2],
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
            )
            triplet_report.append(
                {
                    "triplet_index": idx,
                    "flow": flow_m,
                    "persistence": persist_m,
                }
            )

        summary = summarize_rows(triplet_metrics)
        summary.update(
            {
                "window_start": start,
                "window_end": start + WINDOW_SIZE - 1,
                "first_key": window_keys[0],
                "last_key": window_keys[-1],
                "n_triplets": len(triplet_metrics),
                "flow_wins_mae": int(summary["mean_flow_mae"] < summary["mean_persist_mae"]),
                "flow_wins_rmse": int(summary["mean_flow_rmse"] < summary["mean_persist_rmse"]),
                "flow_wins_csi10": int(summary["mean_flow_csi10"] > summary["mean_persist_csi10"]),
                "flow_wins_csi20": int(summary["mean_flow_csi20"] > summary["mean_persist_csi20"]),
                "flow_wins_csi30": int(summary["mean_flow_csi30"] > summary["mean_persist_csi30"]),
            }
        )
        rows.append(summary)
        triplet_rows.append(
            {
                "window_start": start,
                "window_end": start + WINDOW_SIZE - 1,
                "triplets": triplet_report,
            }
        )

    if not rows:
        raise RuntimeError("No valid windows found")

    out_dir = ROOT / "results" / "nexrad_external"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = ROOT / "figures" / "main"
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows).sort_values("window_start")
    df.to_csv(out_dir / f"{RUN_NAME}_summary.csv", index=False, encoding="utf-8-sig")
    (out_dir / f"{RUN_NAME}_summary.json").write_text(
        json.dumps({"bucket": BUCKET_NAME, "prefix": PREFIX, "windows": rows, "triplets": triplet_rows}, indent=2),
        encoding="utf-8-sig",
    )

    # Pick the most balanced window by counting metric wins; ties favor the one with better mean CSI10.
    df["metric_wins"] = (
        df["flow_wins_mae"]
        + df["flow_wins_rmse"]
        + df["flow_wins_csi10"]
        + df["flow_wins_csi20"]
        + df["flow_wins_csi30"]
    )
    best_row = df.sort_values(
        by=["metric_wins", "mean_flow_csi10", "mean_flow_csi20", "mean_flow_mae"],
        ascending=[False, False, False, True],
    ).iloc[0]

    lines = [
        "# NEXRAD KMRX Window Sweep Farneback Baseline",
        "",
        f"- bucket: {BUCKET_NAME}",
        f"- prefix: {PREFIX}",
        f"- window_starts: {WINDOW_STARTS}",
        f"- selected_window_start: {int(best_row['window_start'])}",
        f"- selected_window_end: {int(best_row['window_end'])}",
        "",
    ]
    for _, row in df.iterrows():
        lines.append(
            f"- start={int(row['window_start'])}: "
            f"flow_mae={row['mean_flow_mae']:.4f} persist_mae={row['mean_persist_mae']:.4f} "
            f"flow_rmse={row['mean_flow_rmse']:.4f} persist_rmse={row['mean_persist_rmse']:.4f} "
            f"flow_csi10={row['mean_flow_csi10']:.4f} persist_csi10={row['mean_persist_csi10']:.4f} "
            f"flow_csi20={row['mean_flow_csi20']:.4f} persist_csi20={row['mean_persist_csi20']:.4f}"
        )

    lines.extend(
        [
            "",
            "## Selected Window",
            f"- start: {int(best_row['window_start'])}",
            f"- end: {int(best_row['window_end'])}",
            f"- metric_wins: {int(best_row['metric_wins'])}/5",
            f"- mean_flow_mae: {best_row['mean_flow_mae']:.4f}",
            f"- mean_persist_mae: {best_row['mean_persist_mae']:.4f}",
            f"- mean_flow_rmse: {best_row['mean_flow_rmse']:.4f}",
            f"- mean_persist_rmse: {best_row['mean_persist_rmse']:.4f}",
            f"- mean_flow_csi10: {best_row['mean_flow_csi10']:.4f}",
            f"- mean_persist_csi10: {best_row['mean_persist_csi10']:.4f}",
            f"- mean_flow_csi20: {best_row['mean_flow_csi20']:.4f}",
            f"- mean_persist_csi20: {best_row['mean_persist_csi20']:.4f}",
        ]
    )
    (log_dir / f"{RUN_NAME}_20260713.md").write_text("\n".join(lines), encoding="utf-8-sig")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharex=True)
    x = df["window_start"].astype(int).to_numpy()
    axes[0].plot(x, df["mean_flow_mae"], marker="o", label="Farneback", color="#2a9d8f")
    axes[0].plot(x, df["mean_persist_mae"], marker="o", label="Persistence", color="#e76f51")
    axes[0].set_title("Mean MAE across selected windows")
    axes[0].set_xlabel("Window start index")
    axes[0].set_ylabel("dBZ")
    axes[0].legend()

    axes[1].plot(x, df["mean_flow_csi10"], marker="o", label="Farneback CSI10", color="#264653")
    axes[1].plot(x, df["mean_persist_csi10"], marker="o", label="Persistence CSI10", color="#f4a261")
    axes[1].plot(x, df["mean_flow_csi20"], marker="o", label="Farneback CSI20", color="#2a9d8f")
    axes[1].plot(x, df["mean_persist_csi20"], marker="o", label="Persistence CSI20", color="#e76f51")
    axes[1].set_title("Threshold skill across selected windows")
    axes[1].set_xlabel("Window start index")
    axes[1].set_ylabel("CSI")
    axes[1].legend(fontsize=8)

    fig.suptitle("NEXRAD KMRX window sweep on 2019-05-20")
    fig.tight_layout()
    fig.savefig(fig_dir / f"figure11_{RUN_NAME}.svg", dpi=160)
    plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
