from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
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


def evaluate_items(items: list[dict[str, Any]], model: MinimalTrainableTPSSCS, pfas: list[float]) -> list[dict[str, Any]]:
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


def group_items_by_subset(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault(item["subset"], []).append(item)
    return grouped


def train_fold(
    train_items: list[dict[str, Any]],
    test_items: list[dict[str, Any]],
    rank: int,
    hidden: int,
    steps: int,
    lr: float,
    seed: int,
    pfas: list[float],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    torch.manual_seed(seed)
    np.random.seed(seed)

    model = MinimalTrainableTPSSCS(rank=rank, hidden=hidden)
    optimizer = torch.optim.Adam(model.gate_net.parameters(), lr=lr)

    curve_rows: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, Any]] = []

    def record(step: int) -> None:
        for split_name, split_items in [("train", train_items), ("test", test_items)]:
            stats = [item_losses(item, model) for item in split_items]
            if stats:
                snapshot_rows.append(
                    {
                        "held_out_subset": test_items[0]["subset"],
                        "seed": seed,
                        "step": step,
                        "split": split_name,
                        "loss": float(np.mean([s["loss"] for s in stats])),
                        "bce": float(np.mean([s["bce"] for s in stats])),
                        "margin": float(np.mean([s["margin"] for s in stats])),
                        "gate_mean": float(np.mean([s["gate_mean"] for s in stats])),
                        "gate_target_mean": float(np.nanmean([s["gate_target_mean"] for s in stats])),
                        "gate_bg_mean": float(np.mean([s["gate_bg_mean"] for s in stats])),
                        "gate_gap": float(np.nanmean([s["gate_gap"] for s in stats])),
                        "n_items": len(split_items),
                        "rank": rank,
                        "hidden": hidden,
                        "lr": lr,
                    }
                )
        for split_name, split_items in [("train", train_items), ("test", test_items)]:
            curve_rows.extend(
                [{**row, "step": step, "split": split_name, "held_out_subset": test_items[0]["subset"], "seed": seed} for row in evaluate_items(split_items, model, pfas)]
            )

    record(0)
    for step in range(1, steps + 1):
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

        if step == steps:
            record(step)

    return curve_rows, snapshot_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "第三批3"))
    parser.add_argument("--rank", type=int, default=30)
    parser.add_argument("--hidden", type=int, default=16)
    parser.add_argument("--steps", type=int, default=150)
    parser.add_argument("--lr", type=float, default=0.02)
    parser.add_argument("--seeds", default="7,11,23")
    parser.add_argument("--pfas", default="1e-4,1e-3,1e-2")
    parser.add_argument("--held_out_subsets", default="simMed,simNoiseOnly,simWind")
    args = parser.parse_args()

    root = Path(args.root)
    ds = AISTAPSampleDataset(root)
    items = collect_items(ds)
    grouped = group_items_by_subset(items)

    held_out_subsets = [x.strip() for x in args.held_out_subsets.split(",") if x.strip()]
    seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
    pfas = [float(x.strip()) for x in args.pfas.split(",") if x.strip()]

    all_curve_rows: list[dict[str, Any]] = []
    all_snapshot_rows: list[dict[str, Any]] = []

    for held_out in held_out_subsets:
        if held_out not in grouped:
            raise KeyError(f"Held-out subset {held_out!r} not present in dataset")
        test_items = grouped[held_out]
        train_items = [item for subset, subset_items in grouped.items() if subset != held_out for item in subset_items]
        for seed in seeds:
            curve_rows, snapshot_rows = train_fold(
                train_items=train_items,
                test_items=test_items,
                rank=args.rank,
                hidden=args.hidden,
                steps=args.steps,
                lr=args.lr,
                seed=seed,
                pfas=pfas,
            )
            all_curve_rows.extend(curve_rows)
            all_snapshot_rows.extend(snapshot_rows)

    result_dir = root / "results" / "aistap_sample"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = root / "figures" / "main"
    fig_dir.mkdir(parents=True, exist_ok=True)

    curve_df = pd.DataFrame(all_curve_rows)
    snap_df = pd.DataFrame(all_snapshot_rows)
    tag = f"rank{args.rank}_hidden{args.hidden}_steps{args.steps}_lr{str(args.lr).replace('.', 'p')}"

    curves_csv = result_dir / f"aistap_subset_loso_cross_condition_{tag}.csv"
    curves_json = result_dir / f"aistap_subset_loso_cross_condition_{tag}.json"
    summary_md = log_dir / "aistap_subset_loso_cross_condition_20260713.md"
    fig_path = fig_dir / "figure4_subset_loso_cross_condition.svg"

    curve_df.to_csv(curves_csv, index=False, encoding="utf-8-sig")
    curves_json.write_text(json.dumps(all_curve_rows, ensure_ascii=False, indent=2), encoding="utf-8-sig")

    agg = (
        curve_df[curve_df["split"] == "test"]
        .groupby(["held_out_subset", "method", "pfa_target"])
        .agg(
            pd_mean=("pd", "mean"),
            pd_std=("pd", "std"),
            pfa_mean=("empirical_pfa", "mean"),
            pfa_std=("empirical_pfa", "std"),
            n_runs=("pd", "count"),
        )
        .reset_index()
    )
    agg.to_csv(result_dir / f"aistap_subset_loso_cross_condition_{tag}_summary.csv", index=False, encoding="utf-8-sig")
    (result_dir / f"aistap_subset_loso_cross_condition_{tag}_summary.json").write_text(
        json.dumps(agg.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )

    summary_lines = [
        "AISTAP subset leave-one-subset-out cross-condition evaluation",
        f"Root: {root}",
        f"Subsets: {', '.join(held_out_subsets)}",
        f"Seeds: {', '.join(map(str, seeds))}",
        f"Hyperparams: rank={args.rank}, hidden={args.hidden}, steps={args.steps}, lr={args.lr}",
        "",
        "Dataset balance:",
    ]
    for subset, subset_items in grouped.items():
        summary_lines.append(f"- {subset}: {len(subset_items)} images")
    summary_lines.append("")
    summary_lines.append("Hold-out summary at test time:")
    for _, row in agg.sort_values(["held_out_subset", "method", "pfa_target"]).iterrows():
        pd_std = "nan" if pd.isna(row["pd_std"]) else f"{row['pd_std']:.4f}"
        pfa_std = "nan" if pd.isna(row["pfa_std"]) else f"{row['pfa_std']:.4f}"
        summary_lines.append(
            f"- holdout={row['held_out_subset']} method={row['method']} pfa={row['pfa_target']:.0e} Pd={row['pd_mean']:.4f}±{pd_std} Pfa={row['pfa_mean']:.4f}±{pfa_std}"
        )
    summary_lines.append("")
    summary_lines.append("Snapshot summary:")
    for _, row in snap_df.sort_values(["held_out_subset", "seed", "split", "step"]).iterrows():
        summary_lines.append(
            f"- holdout={row['held_out_subset']} seed={row['seed']} split={row['split']} step={row['step']} loss={row['loss']:.4f} gate_gap={row['gate_gap']:.4f}"
        )
    summary_md.write_text("\n".join(summary_lines), encoding="utf-8-sig")

    fig, axes = plt.subplots(1, len(pfas), figsize=(5 * len(pfas), 4), sharey=True)
    if len(pfas) == 1:
        axes = [axes]
    methods = ["raw", "low_rank_residual", "trainable_gate"]
    colors = {"raw": "#a8682a", "low_rank_residual": "#3b7ddd", "trainable_gate": "#2e8b57"}
    x = np.arange(len(held_out_subsets))
    width = 0.24
    for ax, pfa in zip(axes, pfas):
        for j, method in enumerate(methods):
            sub = agg[(agg["method"] == method) & (agg["pfa_target"] == pfa)].set_index("held_out_subset").reindex(held_out_subsets)
            vals = sub["pd_mean"].to_numpy(dtype=float)
            errs = sub["pd_std"].fillna(0.0).to_numpy(dtype=float)
            ax.bar(x + (j - 1) * width, vals, width=width, label=method if pfa == pfas[0] else None, color=colors[method], alpha=0.92)
            ax.errorbar(x + (j - 1) * width, vals, yerr=errs, fmt="none", ecolor="black", elinewidth=0.8, capsize=3)
        ax.set_xticks(x)
        ax.set_xticklabels(held_out_subsets, rotation=15)
        ax.set_ylim(0, 1.05)
        ax.set_title(f"Test Pd at Pfa={pfa:.0e}")
        ax.grid(True, axis="y", alpha=0.25)
        ax.set_ylabel("Pd")
    axes[0].legend(loc="lower left", fontsize=8)
    fig.suptitle("AISTAP leave-one-subset-out cross-condition generalization")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=160)
    plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
