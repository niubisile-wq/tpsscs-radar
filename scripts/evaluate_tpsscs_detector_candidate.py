from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tpsscs import AISTAPSampleDataset
from evaluate_aistap_target_preservation_ablation import MinimalTrainableTPSSCS, load_trainable_model


def score_map(x: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(x) ** 2, axis=0)


def conservative_cfar_threshold(bg: np.ndarray, pfa: float) -> tuple[float, int]:
    bg = np.asarray(bg).reshape(-1)
    if bg.size == 0:
        return float("nan"), 0
    max_false_alarms = int(np.floor(float(pfa) * bg.size))
    if max_false_alarms <= 0:
        return float(np.max(bg)), 0
    if max_false_alarms >= bg.size:
        return float(np.nextafter(np.min(bg), -np.inf)), int(bg.size)
    threshold_index = bg.size - max_false_alarms - 1
    threshold = float(np.partition(bg, threshold_index)[threshold_index])
    return threshold, max_false_alarms


def target_mask(meta: dict[str, Any], shape: tuple[int, int]) -> np.ndarray:
    ntrue = meta.get("Ntrue")
    try:
        ntrue_scalar = float(np.asarray(ntrue).reshape(-1)[0]) if ntrue is not None else 0.0
    except Exception:
        ntrue_scalar = 0.0
    if ntrue_scalar <= 0:
        return np.zeros(shape, dtype=bool)

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


def summarize(score: np.ndarray, mask: np.ndarray, pfas: list[float]) -> list[dict[str, Any]]:
    bg = score[~mask]
    tgt = score[mask]
    rows: list[dict[str, Any]] = []
    for pfa in pfas:
        threshold, max_false_alarms = conservative_cfar_threshold(bg, pfa)
        det = score > threshold
        false_alarms = int(det[~mask].sum()) if bg.size else 0
        rows.append(
            {
                "pfa_target": float(pfa),
                "threshold": threshold,
                "pd": float(det[mask].mean()) if tgt.size else float("nan"),
                "empirical_pfa": float(det[~mask].mean()) if bg.size else float("nan"),
                "target_count": int(tgt.size),
                "background_count": int(bg.size),
                "max_false_alarms": int(max_false_alarms),
                "false_alarms": false_alarms,
                "detections": int(det.sum()),
                "threshold_policy": "conservative_topk_strict_gt",
            }
        )
    return rows


def summarize_finished_detector(
    residual_score: np.ndarray, gate_score: np.ndarray, mask: np.ndarray, pfas: list[float]
) -> list[dict[str, Any]]:
    residual_bg = residual_score[~mask]
    gate_bg = gate_score[~mask]
    tgt = residual_score[mask]
    rows: list[dict[str, Any]] = []
    gate_threshold, gate_max_false_alarms = conservative_cfar_threshold(gate_bg, 0.0)
    gate_det = gate_score > gate_threshold
    for pfa in pfas:
        residual_threshold, residual_max_false_alarms = conservative_cfar_threshold(residual_bg, pfa)
        residual_det = residual_score > residual_threshold
        det = residual_det | gate_det
        false_alarms = int(det[~mask].sum()) if residual_bg.size else 0
        rows.append(
            {
                "pfa_target": float(pfa),
                "threshold": float("nan"),
                "residual_threshold": residual_threshold,
                "gate_threshold": gate_threshold,
                "pd": float(det[mask].mean()) if tgt.size else float("nan"),
                "empirical_pfa": float(det[~mask].mean()) if residual_bg.size else float("nan"),
                "target_count": int(tgt.size),
                "background_count": int(residual_bg.size),
                "max_false_alarms": int(residual_max_false_alarms + gate_max_false_alarms),
                "false_alarms": false_alarms,
                "detections": int(det.sum()),
                "threshold_policy": "residual_cfar_plus_zero_false_gate_union",
            }
        )
    return rows


def low_rank_residual(x: np.ndarray, rank: int) -> np.ndarray:
    cdr = x.reshape(x.shape[0] * x.shape[1], x.shape[2])
    u, s, vh = np.linalg.svd(cdr, full_matrices=False)
    k = min(rank, s.shape[0])
    approx = (u[:, :k] * s[:k]) @ vh[:k, :]
    return (cdr - approx).reshape(x.shape)


def evaluate(root: Path, model: MinimalTrainableTPSSCS, pfas: list[float], lowrank_rank: int) -> pd.DataFrame:
    ds = AISTAPSampleDataset(root)
    rows: list[dict[str, Any]] = []
    model.eval()
    with torch.no_grad():
        for item in ds:
            x = item["x"]
            x_np = x.detach().cpu().numpy()
            mask = target_mask(item["metadata"], score_map(x_np).shape)
            if not mask.any():
                continue
            raw = score_map(x_np)
            low = score_map(low_rank_residual(x_np, lowrank_rank))
            out = model(x)
            gate = out["score"].detach().cpu().numpy()
            method_rows: list[tuple[str, list[dict[str, Any]]]] = []
            for method, score in [
                ("raw", raw),
                (f"low_rank_residual_k{lowrank_rank}", low),
                ("tpsscs_trainable_gate", gate),
            ]:
                method_rows.append((method, summarize(score, mask, pfas)))
            method_rows.append(("tpsscs_finished_detector", summarize_finished_detector(low, gate, mask, pfas)))
            for method, method_summary in method_rows:
                for row in method_summary:
                    row.update(
                        {
                            "subset": item["subset"],
                            "image_index": item["image_index"],
                            "path": item["path"],
                            "item_id": f"{item['path']}#{item['image_index']}",
                            "method": method,
                        }
                    )
                    rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "第三批3"))
    parser.add_argument("--state", required=True)
    parser.add_argument("--lowrank-rank", type=int, default=30)
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--tag", default="20260715")
    args = parser.parse_args()

    root = Path(args.root)
    state_path = Path(args.state)
    if not state_path.is_absolute():
        state_path = root / state_path
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    model = load_trainable_model(state_path)
    df = evaluate(root, model, pfas, args.lowrank_rank)

    result_dir = root / "results" / "aistap_sample"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    csv_path = result_dir / f"tpsscs_detector_candidate_{args.tag}.csv"
    json_path = result_dir / f"tpsscs_detector_candidate_{args.tag}.json"
    note_path = log_dir / f"tpsscs_detector_candidate_{args.tag}.md"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    summary = (
        df.groupby(["method", "pfa_target"])
        .agg(
            pd_mean=("pd", "mean"),
            pd_std=("pd", "std"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_items=("item_id", "nunique"),
        )
        .reset_index()
        if not df.empty
        else pd.DataFrame()
    )
    json_path.write_text(
        json.dumps(
            {
                "state": str(state_path),
                "lowrank_rank": args.lowrank_rank,
                "rows": df.to_dict(orient="records"),
                "summary": summary.to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# TP-SSCS Detector Candidate Evaluation",
        "",
        f"Date: {args.tag}",
        "",
        "## Setup",
        "",
        f"- State: `{state_path}`",
        f"- Low-rank comparator: `k={args.lowrank_rank}`",
        f"- Evaluated target-bearing items: `{df['item_id'].nunique() if not df.empty else 0}`",
        "- CFAR threshold policy: `conservative_topk_strict_gt` (`score > threshold`; per-item false alarms are capped at `floor(Pfa * background_count)`).",
        "- Finished detector policy: `residual_cfar_plus_zero_false_gate_union` (rank-matched residual CFAR plus a trainable-gate head that is admitted only above its background maximum).",
        "",
        "## Detection Summary",
        "",
        "| Method | Pfa | Pd mean | Empirical Pfa mean | Items |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in summary.sort_values(["method", "pfa_target"]).iterrows():
        lines.append(
            f"| {row['method']} | {row['pfa_target']:.0e} | {row['pd_mean']:.4f} | {row['empirical_pfa_mean']:.4f} | {int(row['n_items'])} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a public-sample detector-candidate evaluation.",
            "- It proves a reusable model-state-to-CFAR evaluation path.",
            "- It does not by itself prove finished-detector status, cross-dataset superiority, or CAS一区 top readiness.",
        ]
    )
    note_path.write_text("\n".join(lines), encoding="utf-8")

    print(csv_path)
    print(json_path)
    print(note_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
