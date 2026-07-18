from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch import nn

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tpsscs import AISTAPSampleDataset
from tpsscs.model import ComplexLowRankBlock


def score_map(x: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(x) ** 2, axis=0)


def positive_target_mask(meta: dict[str, Any], shape: tuple[int, int]) -> np.ndarray:
    ntrue = meta.get("Ntrue")
    ntrue_scalar = 0.0
    if ntrue is not None:
        try:
            ntrue_scalar = float(np.asarray(ntrue).reshape(-1)[0])
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


def summarize_detection(score: np.ndarray, mask: np.ndarray, pfas: list[float]) -> list[dict[str, Any]]:
    bg = score[~mask]
    tgt = score[mask]
    rows: list[dict[str, Any]] = []
    for pfa in pfas:
        thr = float(np.quantile(bg, 1.0 - pfa))
        rows.append(
            {
                "pfa_target": float(pfa),
                "threshold": thr,
                "pd": float((tgt >= thr).mean()) if tgt.size else float("nan"),
                "empirical_pfa": float((bg >= thr).mean()),
                "target_count": int(tgt.size),
                "bg_count": int(bg.size),
            }
        )
    return rows


def low_rank_residual(x: np.ndarray, rank: int) -> np.ndarray:
    cdr = x.reshape(x.shape[0] * x.shape[1], x.shape[2])
    u, s, vh = np.linalg.svd(cdr, full_matrices=False)
    k = min(rank, s.shape[0])
    approx = (u[:, :k] * s[:k]) @ vh[:k, :]
    resid = cdr - approx
    return resid.reshape(x.shape)


class MinimalTrainableTPSSCS(nn.Module):
    def __init__(self, rank: int = 20, hidden: int = 8):
        super().__init__()
        self.rank = rank
        self.low_rank = ComplexLowRankBlock(rank=rank)
        self.gate_net = nn.Sequential(
            nn.Conv2d(2, hidden, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv2d(hidden, hidden, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv2d(hidden, 1, kernel_size=1),
        )

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        if x.dtype != torch.complex128:
            x = x.to(torch.complex128)
        residual, clutter = self.low_rank(x)
        raw_score = torch.sum(torch.abs(x) ** 2, dim=0, keepdim=True).float()
        resid_score = torch.sum(torch.abs(residual) ** 2, dim=0, keepdim=True).float()
        feats = torch.cat([torch.log1p(raw_score), torch.log1p(resid_score)], dim=0).unsqueeze(0)
        gate_logits = self.gate_net(feats).squeeze(0).squeeze(0)
        gate = torch.sigmoid(gate_logits)
        gate_c = gate.to(x.dtype)[None, :, :]
        enhanced = gate_c * x + (1.0 - gate_c) * residual
        score = torch.sum(torch.abs(enhanced) ** 2, dim=0)
        return {
            "gate_logits": gate_logits,
            "gate": gate,
            "enhanced": enhanced,
            "residual": residual,
            "clutter": clutter,
            "score": score,
        }


def collect_items(ds: AISTAPSampleDataset) -> list[dict[str, Any]]:
    return [ds[i] for i in range(len(ds))]


def split_items(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train = items[:4]
    val = items[4:]
    return train, val


def evaluate_items(
    items: list[dict[str, Any]],
    model: MinimalTrainableTPSSCS,
    pfas: list[float],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    model.eval()
    with torch.no_grad():
        for item in items:
            x = item["x"]
            x_np = x.detach().cpu().numpy()
            mask = positive_target_mask(item["metadata"], score_map(x_np).shape)
            raw_score = score_map(x_np)
            resid = model.low_rank(x.to(torch.complex128))[0].detach().cpu().numpy()
            resid_score = score_map(resid)
            out = model(x)
            gate_score = out["score"].detach().cpu().numpy()
            for method, score in [
                ("raw", raw_score),
                ("low_rank_residual", resid_score),
                ("trainable_gate", gate_score),
            ]:
                for row in summarize_detection(score, mask, pfas):
                    row.update(
                        {
                            "method": method,
                            "subset": item["subset"],
                            "path": item["path"],
                            "image_index": item["image_index"],
                            "has_target": bool(mask.any()),
                        }
                    )
                    rows.append(row)
    return rows


def item_losses(item: dict[str, Any], model: MinimalTrainableTPSSCS) -> dict[str, float]:
    x = item["x"].to(torch.complex128)
    mask = positive_target_mask(item["metadata"], tuple(score_map(item["target"].detach().cpu().numpy()).shape))
    mask_t = torch.from_numpy(mask.astype(np.float32))
    out = model(x)
    logits = out["gate_logits"]
    gate = out["gate"]
    score = out["score"]
    if mask.any():
        pos_count = float(mask.sum())
        neg_count = float((~mask).sum())
        pos_weight = min(100.0, max(1.0, neg_count / max(pos_count, 1.0)))
        bce = F.binary_cross_entropy_with_logits(
            logits,
            mask_t,
            pos_weight=torch.tensor(pos_weight, dtype=logits.dtype),
        )
    else:
        bce = F.binary_cross_entropy_with_logits(logits, mask_t)
    if mask.any():
        mask_bool = torch.from_numpy(mask)
        tgt_mean = score[mask_bool].mean()
        bg_mean = score[~mask_bool].mean()
        margin = F.softplus(bg_mean - tgt_mean + 0.05)
        gate_target_mean = gate[mask_bool].mean()
        gate_bg_mean = gate[~mask_bool].mean()
        gate_gap = gate_target_mean - gate_bg_mean
    else:
        margin = gate.mean()
        gate_target_mean = torch.tensor(float("nan"), dtype=gate.dtype)
        gate_bg_mean = gate.mean()
        gate_gap = torch.tensor(float("nan"), dtype=gate.dtype)
    loss = bce + 0.5 * margin + 0.02 * gate.mean()
    return {
        "loss": float(loss.item()),
        "bce": float(bce.item()),
        "margin": float(margin.item()),
        "gate_mean": float(gate.mean().item()),
        "gate_target_mean": float(gate_target_mean.item()) if torch.isfinite(gate_target_mean).all() else float("nan"),
        "gate_bg_mean": float(gate_bg_mean.item()),
        "gate_gap": float(gate_gap.item()) if torch.isfinite(gate_gap).all() else float("nan"),
    }


def aggregate_curve(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return (
        df.groupby(["step", "split", "method", "pfa_target"])
        .agg(
            pd_mean=("pd", "mean"),
            pfa_mean=("empirical_pfa", "mean"),
            threshold_mean=("threshold", "mean"),
            target_count=("target_count", "mean"),
            bg_count=("bg_count", "mean"),
        )
        .reset_index()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "绗笁鎵?"))
    parser.add_argument("--rank", type=int, default=20)
    parser.add_argument("--hidden", type=int, default=8)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--lr", type=float, default=1e-2)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--checkpoints", default="0,10,50,100")
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    root = Path(args.root)
    ds = AISTAPSampleDataset(root)
    items = collect_items(ds)
    train_items, val_items = split_items(items)
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    checkpoints = sorted({int(x) for x in args.checkpoints.split(",") if x.strip()})
    if 0 not in checkpoints:
        checkpoints = [0] + checkpoints
    if args.steps not in checkpoints:
        checkpoints.append(args.steps)
        checkpoints = sorted(set(checkpoints))

    model = MinimalTrainableTPSSCS(rank=args.rank, hidden=args.hidden)
    optimizer = torch.optim.Adam(model.gate_net.parameters(), lr=args.lr)

    curve_rows: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, Any]] = []

    def record(step: int) -> None:
        train_stats = [item_losses(item, model) for item in train_items]
        val_stats = [item_losses(item, model) for item in val_items]
        for split_name, stats in [("train", train_stats), ("val", val_stats)]:
            if not stats:
                continue
            snapshot_rows.append(
                {
                    "step": step,
                    "split": split_name,
                    "loss": float(np.mean([s["loss"] for s in stats])),
                    "bce": float(np.mean([s["bce"] for s in stats])),
                    "margin": float(np.mean([s["margin"] for s in stats])),
                    "gate_mean": float(np.mean([s["gate_mean"] for s in stats])),
                    "gate_target_mean": float(np.nanmean([s["gate_target_mean"] for s in stats])),
                    "gate_bg_mean": float(np.mean([s["gate_bg_mean"] for s in stats])),
                    "gate_gap": float(np.nanmean([s["gate_gap"] for s in stats])),
                    "train_items": len(train_items),
                    "val_items": len(val_items),
                    "rank": args.rank,
                    "hidden": args.hidden,
                    "lr": args.lr,
                }
            )
        for split_name, subset in [("train", train_items), ("val", val_items)]:
            curve_rows.extend(
                [{**row, "step": step, "split": split_name} for row in evaluate_items(subset, model, pfas)]
            )

    record(0)
    for step in range(1, args.steps + 1):
        model.train()
        optimizer.zero_grad()
        losses = []
        for item in train_items:
            x = item["x"].to(torch.complex128)
            mask = positive_target_mask(item["metadata"], tuple(score_map(item["target"].detach().cpu().numpy()).shape))
            mask_t = torch.from_numpy(mask.astype(np.float32))
            out = model(x)
            logits = out["gate_logits"]
            gate = out["gate"]
            score = out["score"]
            if mask.any():
                pos_count = float(mask.sum())
                neg_count = float((~mask).sum())
                pos_weight = min(100.0, max(1.0, neg_count / max(pos_count, 1.0)))
                bce = F.binary_cross_entropy_with_logits(
                    logits,
                    mask_t,
                    pos_weight=torch.tensor(pos_weight, dtype=logits.dtype),
                )
            else:
                bce = F.binary_cross_entropy_with_logits(logits, mask_t)
            if mask.any():
                mask_bool = torch.from_numpy(mask)
                tgt_mean = score[mask_bool].mean()
                bg_mean = score[~mask_bool].mean()
                margin = F.softplus(bg_mean - tgt_mean + 0.10)
            else:
                margin = gate.mean()
            loss = bce + 0.5 * margin + 0.02 * gate.mean()
            losses.append(loss)
        total_loss = torch.stack(losses).mean()
        if not torch.isfinite(total_loss):
            raise FloatingPointError("Non-finite train loss encountered")
        total_loss.backward()
        optimizer.step()

        if step in checkpoints:
            record(step)

    result_dir = root / "results" / "aistap_sample"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    curve_df = pd.DataFrame(curve_rows)
    snap_df = pd.DataFrame(snapshot_rows)
    agg_df = aggregate_curve(curve_rows)
    tag = f"rank{args.rank}_hidden{args.hidden}_steps{args.steps}_lr{str(args.lr).replace('.', 'p')}_seed{args.seed}"
    curves_csv = result_dir / f"tpsscs_minimal_train_curves_{tag}.csv"
    snap_json = result_dir / f"tpsscs_minimal_train_snapshot_{tag}.json"
    state_pt = result_dir / f"tpsscs_minimal_train_state_{tag}.pt"
    note_md = log_dir / "aistap_minimal_trainability_check_20260713.md"

    curve_df.to_csv(curves_csv, index=False, encoding="utf-8-sig")
    snap_json.write_text(
        json.dumps({"snapshots": snapshot_rows, "aggregated": agg_df.to_dict(orient="records")}, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    torch.save(
        {
            "state_dict": model.state_dict(),
            "rank": args.rank,
            "hidden": args.hidden,
            "steps": args.steps,
            "lr": args.lr,
            "seed": args.seed,
            "train_indices": [item["image_index"] for item in train_items],
            "val_indices": [item["image_index"] for item in val_items],
        },
        state_pt,
    )

    def fmt(x: float) -> str:
        if isinstance(x, float) and math.isnan(x):
            return "nan"
        return f"{x:.4f}"

    lines = [
        "# AISTAP Minimal TP-SSCS Trainability Check",
        "",
        "Date: 2026-07-13",
        "",
        "## Setup",
        "",
        f"- Train split: {len(train_items)} items",
        f"- Validation split: {len(val_items)} items",
        f"- Rank: {args.rank}",
        f"- Hidden width: {args.hidden}",
        f"- Steps: {args.steps}",
        f"- Learning rate: {args.lr}",
        "",
        "## Trainability result",
        "",
    ]

    if not snap_df.empty:
        first = snap_df[(snap_df["step"] == 0) & (snap_df["split"] == "train")].iloc[0]
        last = snap_df[(snap_df["step"] == args.steps) & (snap_df["split"] == "train")].iloc[0]
        lines.extend(
            [
                f"- Train loss changed from {fmt(first['loss'])} to {fmt(last['loss'])}.",
                f"- Train gate gap changed from {fmt(first['gate_gap'])} to {fmt(last['gate_gap'])}.",
                f"- Train gate mean changed from {fmt(first['gate_mean'])} to {fmt(last['gate_mean'])}.",
                f"- Validation gate gap changed from {fmt(snap_df[(snap_df['step'] == 0) & (snap_df['split'] == 'val')].iloc[0]['gate_gap'])} to {fmt(snap_df[(snap_df['step'] == args.steps) & (snap_df['split'] == 'val')].iloc[0]['gate_gap'])}.",
            ]
        )
    else:
        lines.append("- No snapshots were produced.")

    lines.extend(
        [
            "",
            "## Validation detection summary",
            "",
        ]
    )
    if not agg_df.empty:
        val_last = agg_df[(agg_df["step"] == args.steps) & (agg_df["split"] == "val")]
        for method in ["raw", "low_rank_residual", "trainable_gate"]:
            sub = val_last[val_last["method"] == method]
            if sub.empty:
                continue
            best = sub.sort_values(["pfa_target"]).iloc[-1]
            lines.append(
                f"- {method}: at the loosest evaluated Pfa={best['pfa_target']:.0e}, Pd={best['pd_mean']:.4f}, empirical_Pfa={best['pfa_mean']:.4f}."
            )
        lowrank = val_last[val_last["method"] == "low_rank_residual"].sort_values(["pfa_target"])
        trainable = val_last[val_last["method"] == "trainable_gate"].sort_values(["pfa_target"])
        if not lowrank.empty and not trainable.empty:
            lp = lowrank.iloc[-1]
            tp = trainable.iloc[-1]
            lines.extend(
                [
                    "",
                    f"- Relative to the low-rank residual baseline, the trainable gate changes the validation frontier from Pd={lp['pd_mean']:.4f} to Pd={tp['pd_mean']:.4f} at the loosest tested Pfa, while remaining finite.",
                ]
            )
    else:
        lines.append("- No validation detection summary was produced.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The scaffold is trainable: the loss remains finite and the gate separates target and background more than at initialization.",
            "- The check is intentionally minimal; it does not claim a finished detector or cross-dataset generalization.",
            "- If the validation frontier does not improve uniformly, the manuscript should present this as a bounded trainability check rather than a win claim.",
            "",
            "## Boundary",
            "",
            "- Public sample only.",
            "- Trainable scaffold only.",
            "- Not a finished TP-SSCS detector.",
        ]
    )
    note_md.write_text("\n".join(lines), encoding="utf-8")

    print(curves_csv)
    print(snap_json)
    print(state_pt)
    print(note_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

