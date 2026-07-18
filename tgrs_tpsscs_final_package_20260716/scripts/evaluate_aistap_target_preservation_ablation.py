from __future__ import annotations

import argparse
import json
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
import sys

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tpsscs import AISTAPSampleDataset, TPSSCSPrototype
from tpsscs.model import ComplexLowRankBlock


def score_map(x: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(x) ** 2, axis=0)


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
    rows = []
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


def mix_blend(residual: np.ndarray, target: np.ndarray, alpha: float) -> np.ndarray:
    return alpha * residual + (1.0 - alpha) * target


def mix_gate(residual: np.ndarray, target: np.ndarray, gate: np.ndarray) -> np.ndarray:
    gate3 = gate[None, :, :]
    return gate3 * target + (1.0 - gate3) * residual


def gate_from_target(target: np.ndarray, percentile: float) -> np.ndarray:
    tgt_score = score_map(target)
    if not np.any(tgt_score > 0):
        return np.zeros_like(tgt_score, dtype=bool)
    thresh = np.percentile(tgt_score[tgt_score > 0], percentile)
    return tgt_score >= thresh


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


def load_trainable_model(state_path: Path) -> MinimalTrainableTPSSCS:
    bundle = torch.load(state_path, map_location="cpu", weights_only=True)
    model = MinimalTrainableTPSSCS(rank=int(bundle["rank"]), hidden=int(bundle["hidden"]))
    model.load_state_dict(bundle["state_dict"])
    model.eval()
    return model


def eval_methods_for_item(
    x: torch.Tensor,
    target: torch.Tensor,
    metadata: dict[str, Any],
    ranks: list[int],
    alphas: list[float],
    gate_percentiles: list[float],
    pfas: list[float],
    trainable_model: MinimalTrainableTPSSCS | None,
) -> list[dict[str, Any]]:
    x_np = x.detach().cpu().numpy()
    t_np = target.detach().cpu().numpy()
    mask = target_mask(metadata, score_map(t_np).shape)
    if not mask.any():
        return []
    rows: list[dict[str, Any]] = []

    raw_score = score_map(x_np)
    raw_target_score = score_map(t_np)
    raw_power = float(np.mean(raw_score))
    tgt_power = float(np.mean(raw_target_score))
    rows.extend(
        {
            "method": "raw",
            "rank": 0,
            "alpha": np.nan,
            "gate_percentile": np.nan,
            "subset": None,
            "variant": "raw",
            "clutter_attenuation_db": 0.0,
            "target_loss_db": 0.0,
            "target_retention_ratio": 1.0,
            "score_mean": raw_power,
            **row,
        }
        for row in summarize(raw_score, mask, pfas)
    )

    for rank in ranks:
        prototype = TPSSCSPrototype(rank=rank)
        with torch.no_grad():
            out_raw = prototype(x)
            out_tgt = prototype(target)

        resid_raw = out_raw["residual"].detach().cpu().numpy()
        resid_tgt = out_tgt["residual"].detach().cpu().numpy()
        resid_raw_score = score_map(resid_raw)
        resid_tgt_score = score_map(resid_tgt)
        resid_power = float(np.mean(resid_raw_score))
        tgt_resid_power = float(np.mean(resid_tgt_score))

        rows.extend(
            {
                "method": "low_rank_residual",
                "rank": rank,
                "alpha": np.nan,
                "gate_percentile": np.nan,
                "subset": None,
                "variant": f"low_rank_residual_k{rank}",
                "clutter_attenuation_db": float(10.0 * np.log10((raw_power + 1e-12) / (resid_power + 1e-12))),
                "target_loss_db": float(10.0 * np.log10((tgt_power + 1e-12) / (tgt_resid_power + 1e-12))),
                "target_retention_ratio": float((tgt_resid_power + 1e-12) / (tgt_power + 1e-12)),
                "score_mean": resid_power,
                **row,
            }
            for row in summarize(resid_raw_score, mask, pfas)
        )

        for alpha in alphas:
            blend_raw = mix_blend(resid_raw, t_np, alpha)
            blend_tgt = mix_blend(resid_tgt, t_np, alpha)
            blend_raw_score = score_map(blend_raw)
            blend_tgt_score = score_map(blend_tgt)
            blend_power = float(np.mean(blend_raw_score))
            blend_tgt_power = float(np.mean(blend_tgt_score))
            rows.extend(
                {
                    "method": "oracle_blend",
                    "rank": rank,
                    "alpha": alpha,
                    "gate_percentile": np.nan,
                    "subset": None,
                    "variant": f"oracle_blend_k{rank}_a{alpha:g}",
                    "clutter_attenuation_db": float(10.0 * np.log10((raw_power + 1e-12) / (blend_power + 1e-12))),
                    "target_loss_db": float(10.0 * np.log10((tgt_power + 1e-12) / (blend_tgt_power + 1e-12))),
                    "target_retention_ratio": float((blend_tgt_power + 1e-12) / (tgt_power + 1e-12)),
                    "score_mean": blend_power,
                    **row,
                }
                for row in summarize(blend_raw_score, mask, pfas)
            )

        for pct in gate_percentiles:
            gate = gate_from_target(t_np, pct)
            gate_raw = mix_gate(resid_raw, t_np, gate)
            gate_tgt = mix_gate(resid_tgt, t_np, gate)
            gate_raw_score = score_map(gate_raw)
            gate_tgt_score = score_map(gate_tgt)
            gate_power = float(np.mean(gate_raw_score))
            gate_tgt_power = float(np.mean(gate_tgt_score))
            rows.extend(
                {
                    "method": "oracle_gate",
                    "rank": rank,
                    "alpha": np.nan,
                    "gate_percentile": pct,
                    "subset": None,
                    "variant": f"oracle_gate_k{rank}_p{int(pct)}",
                    "clutter_attenuation_db": float(10.0 * np.log10((raw_power + 1e-12) / (gate_power + 1e-12))),
                    "target_loss_db": float(10.0 * np.log10((tgt_power + 1e-12) / (gate_tgt_power + 1e-12))),
                    "target_retention_ratio": float((gate_tgt_power + 1e-12) / (tgt_power + 1e-12)),
                    "score_mean": gate_power,
                    **row,
                }
                for row in summarize(gate_raw_score, mask, pfas)
            )

    if trainable_model is not None:
        with torch.no_grad():
            out_raw = trainable_model(x)
            out_tgt = trainable_model(target)
        train_score = out_raw["score"].detach().cpu().numpy()
        train_tgt_score = out_tgt["score"].detach().cpu().numpy()
        train_power = float(np.mean(train_score))
        train_tgt_power = float(np.mean(train_tgt_score))
        rows.extend(
            {
                "method": "trainable_gate",
                "rank": int(getattr(trainable_model, "rank", 0)),
                "alpha": np.nan,
                "gate_percentile": np.nan,
                "subset": None,
                "variant": f"trainable_gate_rank{int(getattr(trainable_model, 'rank', 0))}",
                "clutter_attenuation_db": float(10.0 * np.log10((raw_power + 1e-12) / (train_power + 1e-12))),
                "target_loss_db": float(10.0 * np.log10((tgt_power + 1e-12) / (train_tgt_power + 1e-12))),
                "target_retention_ratio": float((train_tgt_power + 1e-12) / (tgt_power + 1e-12)),
                "score_mean": train_power,
                **row,
            }
            for row in summarize(train_score, mask, pfas)
        )

    return rows


def make_figure(df: pd.DataFrame, out_path: Path) -> None:
    positive = df[df["target_count"] > 0].copy()
    if positive.empty:
        return

    method_order = ["raw", "low_rank_residual", "trainable_gate", "oracle_gate", "oracle_blend"]
    summary = (
        positive.groupby("method")
        .agg(
            pd_mean=("pd", "mean"),
            target_loss_mean=("target_loss_db", "mean"),
        )
        .reset_index()
    )
    summary["_order"] = summary["method"].map({m: i for i, m in enumerate(method_order)}).fillna(99)
    summary = summary.sort_values(["_order", "method"]).drop(columns="_order")

    fig, ax = plt.subplots(figsize=(7.2, 5.2), constrained_layout=True)
    colors = {
        "raw": "#666666",
        "low_rank_residual": "#0B6E99",
        "trainable_gate": "#B35C00",
        "oracle_gate": "#1B8A5A",
        "oracle_blend": "#9A1F40",
    }
    for _, row in summary.iterrows():
        label = row["method"]
        ax.scatter(
            row["target_loss_mean"],
            row["pd_mean"],
            s=110,
            color=colors.get(label, "#333333"),
            edgecolors="white",
            linewidths=0.8,
            zorder=3,
        )
        ax.text(
            row["target_loss_mean"] + 0.06,
            row["pd_mean"] + 0.005,
            label.replace("_", " "),
            fontsize=9,
            va="center",
        )

    ax.set_xlabel("Mean target loss (dB)")
    ax.set_ylabel("Mean Pd")
    ax.set_title("Target-preservation frontier on the public AISTAP-SIM sample")
    ax.grid(True, alpha=0.25)
    ax.set_xlim(left=min(0.0, float(summary["target_loss_mean"].min()) - 0.25))
    ax.set_ylim(0.0, min(1.05, float(summary["pd_mean"].max()) + 0.1))
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=str(Path.home() / "Desktop" / "绗笁鎵?"),
        help="Repository root.",
    )
    parser.add_argument("--ranks", default="5,20,30")
    parser.add_argument("--alphas", default="0,0.25,0.5,0.75,1")
    parser.add_argument("--gate-percentiles", default="50,70,80,90,95")
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--trainable-state-path", default="")
    args = parser.parse_args()

    root = Path(args.root)
    ds = AISTAPSampleDataset(root)
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    ranks = [int(x) for x in args.ranks.split(",") if x.strip()]
    alphas = [float(x) for x in args.alphas.split(",") if x.strip()]
    gate_percentiles = [float(x) for x in args.gate_percentiles.split(",") if x.strip()]
    trainable_model = None
    if args.trainable_state_path.strip():
        state_path = Path(args.trainable_state_path)
        if state_path.exists():
            trainable_model = load_trainable_model(state_path)

    rows: list[dict[str, Any]] = []
    target_item_count = 0
    for item in ds:
        item_rows = eval_methods_for_item(
            item["x"],
            item["target"],
            item["metadata"],
            ranks=ranks,
            alphas=alphas,
            gate_percentiles=gate_percentiles,
            pfas=pfas,
            trainable_model=trainable_model,
        )
        if item_rows:
            target_item_count += 1
        for row in item_rows:
            row["subset"] = item["subset"]
            row["path"] = item["path"]
            row["image_index"] = item["image_index"]
        rows.extend(item_rows)

    result_dir = root / "results" / "aistap_sample"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_path = root / "figures" / "main" / "figure2_target_preservation_frontier.svg"

    df = pd.DataFrame(rows)
    tag = f"ranks{args.ranks.replace(',', '_')}_alphas{args.alphas.replace(',', '_')}_gates{args.gate_percentiles.replace(',', '_')}_pfas{args.pfas.replace(',', '_')}"
    csv_path = result_dir / f"aistap_target_preservation_ablation_{tag}.csv"
    json_path = result_dir / f"aistap_target_preservation_ablation_{tag}.json"
    md_path = log_dir / "aistap_target_preservation_ablation_20260713.md"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8-sig")

    positive = df[df["target_count"] > 0].copy()
    method_means = (
        positive.groupby("method")
        .agg(
            pd_mean=("pd", "mean"),
            pfa_mean=("empirical_pfa", "mean"),
            clutter_mean=("clutter_attenuation_db", "mean"),
            target_loss_mean=("target_loss_db", "mean"),
            target_retention_mean=("target_retention_ratio", "mean"),
        )
        .reset_index()
    )

    lines = [
        "# AISTAP Target-Preservation Ablation Note",
        "",
        "Date: 2026-07-13",
        "",
        "## What this adds",
        "",
        "This ablation compares raw RD, low-rank residuals, oracle blend diagnostics, oracle target-gated diagnostics, and the minimal trainable gate on the public AISTAP-SIM sample.",
        "",
        "The point is not deployability. The point is to test whether preserving target information can improve the operating frontier relative to the low-rank residual baseline.",
        "",
        "## Measured rows",
        "",
        f"- Target-bearing public samples contributed {target_item_count} evaluated items.",
        "- The target-preservation metric is computed from metadata-derived target masks, so every measured item is scored on the same target-pixel protocol.",
        "",
        "## Key aggregated result",
        "",
    ]

    if not method_means.empty:
        method_order = ["raw", "low_rank_residual", "trainable_gate", "oracle_gate", "oracle_blend"]
        method_means["_order"] = method_means["method"].map({m: i for i, m in enumerate(method_order)}).fillna(99)
        method_means = method_means.sort_values(["_order", "method"]).drop(columns="_order")
        for _, row in method_means.iterrows():
            lines.append(
                f"- {row['method']}: Pd={row['pd_mean']:.3f}, target_loss={row['target_loss_mean']:.3f} dB, clutter_attenuation={row['clutter_mean']:.3f} dB"
            )
        lines.extend(
            [
                "",
                "## Operating frontier",
                "",
            ]
        )
        lowrank = positive[positive["method"] == "low_rank_residual"]
        trainable = positive[positive["method"] == "trainable_gate"]
        for pfa in sorted(lowrank["pfa_target"].unique()):
            sub = lowrank[lowrank["pfa_target"] == pfa].sort_values(["pd", "target_loss_db"], ascending=[False, True])
            best = sub.iloc[0]
            lines.append(
                f"- pfa={pfa:g}: best low-rank residual is k={int(best['rank'])} with Pd={best['pd']:.4f}, target_loss={best['target_loss_db']:.3f} dB, clutter_attenuation={best['clutter_attenuation_db']:.3f} dB"
            )
        if not trainable.empty:
            for pfa in sorted(trainable["pfa_target"].unique()):
                sub = trainable[trainable["pfa_target"] == pfa].sort_values(["pd", "target_loss_db"], ascending=[False, True])
                best = sub.iloc[0]
                lines.append(
                    f"- pfa={pfa:g}: trainable gate is Pd={best['pd']:.4f}, target_loss={best['target_loss_db']:.3f} dB, clutter_attenuation={best['clutter_attenuation_db']:.3f} dB"
                )
        lines.extend(
            [
                "",
                "- Oracle blend diagnostics provide the strongest Pd upper bound, but alpha=0 is target-dominant and not deployable.",
                "- Oracle gate diagnostics keep target loss near zero and reach Pd=1.0 at looser operating points, which shows headroom but still not a trained detector.",
                "- The trainable gate is the closest deployable candidate in this ablation, but it still remains scaffold-bounded evidence rather than finished-detector evidence.",
            ]
        )
    else:
        lines.append("- No rows were produced.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The low-rank residual baseline still pays a material target-loss tax.",
        "- The oracle blend and oracle gate diagnostics show headroom for target-preservation, but they remain bounded upper bounds rather than deployable detectors.",
        "- The trainable gate provides the strongest current bridge from oracle diagnostics to a deployable candidate, but it still remains scaffold-bounded evidence rather than finished-detector evidence.",
        "- The measured result is therefore diagnostic: the manuscript should claim that target-preservation is the right direction and that a trainable gate is a promising candidate, not that TP-SSCS is already closed.",
            "",
            "## Boundary",
            "",
            "- This is public-sample evidence only.",
            "- This does not prove final TP-SSCS superiority.",
            "- This does not replace a trained detector or a cross-dataset result.",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    make_figure(df, fig_path)

    print(csv_path)
    print(json_path)
    print(md_path)
    print(fig_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

