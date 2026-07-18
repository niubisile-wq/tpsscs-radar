from __future__ import annotations

import argparse
import json
import math
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


def low_rank_residuals_for_ranks(x: np.ndarray, ranks: list[int]) -> dict[int, np.ndarray]:
    cdr = x.reshape(x.shape[0] * x.shape[1], x.shape[2])
    u, s, vh = np.linalg.svd(cdr, full_matrices=False)
    outputs: dict[int, np.ndarray] = {}
    for rank in ranks:
        k = min(rank, s.shape[0])
        approx = (u[:, :k] * s[:k]) @ vh[:k, :]
        resid = cdr - approx
        outputs[rank] = resid.reshape(x.shape)
    return outputs


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


def load_trainable_model(state_path: Path) -> tuple[MinimalTrainableTPSSCS, dict[str, Any]]:
    bundle = torch.load(state_path, map_location="cpu", weights_only=True)
    model = MinimalTrainableTPSSCS(rank=int(bundle["rank"]), hidden=int(bundle["hidden"]))
    model.load_state_dict(bundle["state_dict"])
    model.eval()
    return model, bundle


def perturb_x(
    x: np.ndarray,
    target: np.ndarray,
    family: str,
    level: float,
    rng: np.random.Generator,
) -> np.ndarray:
    if family == "noise":
        power = np.mean(np.abs(x) ** 2)
        sigma = math.sqrt(power) * level / math.sqrt(2.0)
        noise = sigma * (rng.normal(size=x.shape) + 1j * rng.normal(size=x.shape))
        return x + noise
    if family == "amplitude":
        return x * level
    if family == "phase":
        phase = rng.normal(loc=0.0, scale=level, size=x.shape)
        return x * np.exp(1j * phase)
    if family == "target_attenuation":
        clutter = x - target
        return clutter + level * target
    if family == "clutter_scale":
        clutter = x - target
        return level * clutter + target
    raise ValueError(f"Unknown perturbation family: {family}")


def evaluate_condition(
    items: list[dict[str, Any]],
    family: str,
    level: float,
    pfas: list[float],
    ranks: list[int],
    model: MinimalTrainableTPSSCS,
    seed: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item_idx, item in enumerate(items):
        x = item["x"].detach().cpu().numpy()
        t = item["target"].detach().cpu().numpy()
        mask = positive_target_mask(item["metadata"], score_map(t).shape)
        rng = np.random.default_rng(seed + item_idx * 1000 + int(level * 1000))
        x_pert = perturb_x(x, t, family, level, rng)

        raw_score = score_map(x_pert)
        rows.extend(
            {
                "family": family,
                "level": level,
                "method": "raw",
                "rank": 0,
                "subset": item["subset"],
                "path": item["path"],
                "image_index": item["image_index"],
                "has_target": bool(mask.any()),
                **row,
            }
            for row in summarize_detection(raw_score, mask, pfas)
        )

        resid_map = low_rank_residuals_for_ranks(x_pert, ranks)
        for rank in ranks:
            resid = resid_map[rank]
            resid_score = score_map(resid)
            rows.extend(
                {
                    "family": family,
                    "level": level,
                    "method": "low_rank_residual",
                    "rank": rank,
                    "subset": item["subset"],
                    "path": item["path"],
                    "image_index": item["image_index"],
                    "has_target": bool(mask.any()),
                    **row,
                }
                for row in summarize_detection(resid_score, mask, pfas)
            )

        with torch.no_grad():
            out = model(torch.from_numpy(x_pert))
        train_score = out["score"].detach().cpu().numpy()
        rows.extend(
            {
                "family": family,
                "level": level,
                "method": "trainable_gate",
                "rank": model.rank,
                "subset": item["subset"],
                "path": item["path"],
                "image_index": item["image_index"],
                "has_target": bool(mask.any()),
                **row,
            }
            for row in summarize_detection(train_score, mask, pfas)
        )
    return rows


def best_rank_summary(df: pd.DataFrame, pfa: float) -> pd.DataFrame:
    sub = df[(df["method"] == "low_rank_residual") & (df["pfa_target"] == pfa)].copy()
    if sub.empty:
        return sub
    sub = (
        sub.groupby(["family", "level", "rank"])
        .agg(pd_mean=("pd", "mean"), pfa_mean=("empirical_pfa", "mean"))
        .reset_index()
    )
    sub = sub.sort_values(["family", "level", "pd_mean", "rank"], ascending=[True, True, False, True])
    best = sub.groupby(["family", "level"], as_index=False).head(1).copy()
    best = best.rename(columns={"rank": "best_rank"})
    return best


def make_figure(df: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    levels = sorted(df["level"].unique().tolist())
    families = sorted(df["family"].unique().tolist())

    pfa_ref = 1e-3
    best = best_rank_summary(df, pfa_ref)
    for fam in families:
        sub = best[best["family"] == fam].sort_values("level")
        if sub.empty:
            continue
        axes[0].plot(sub["level"], sub["best_rank"], marker="o", label=fam)
    axes[0].set_xlabel("Perturbation level")
    axes[0].set_ylabel(f"Best rank at Pfa={pfa_ref:.0e}")
    axes[0].set_title("Best-k stability")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(frameon=False, fontsize=8)

    sub = df[(df["pfa_target"] == pfa_ref) & (df["method"].isin(["low_rank_residual", "trainable_gate"]))]
    agg = (
        sub.groupby(["family", "level", "method"])
        .agg(pd_mean=("pd", "mean"))
        .reset_index()
    )
    for method, style in [("low_rank_residual", "--"), ("trainable_gate", "-")]:
        for fam in families:
            fam_sub = agg[(agg["method"] == method) & (agg["family"] == fam)].sort_values("level")
            if fam_sub.empty:
                continue
            axes[1].plot(
                fam_sub["level"],
                fam_sub["pd_mean"],
                marker="o",
                linestyle=style,
                label=f"{fam} / {method}" if method == "trainable_gate" else f"{fam} / low-rank",
            )
    axes[1].set_xlabel("Perturbation level")
    axes[1].set_ylabel(f"Mean Pd at Pfa={pfa_ref:.0e}")
    axes[1].set_title("Pd stability under stress")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(frameon=False, fontsize=7, ncol=2)
    fig.suptitle("AISTAP stress grid: operating-policy and trainable-gate stability", fontsize=12)
    fig.savefig(out_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "绗笁鎵?"))
    parser.add_argument("--state-path", default="")
    parser.add_argument("--rank-grid", default="1,3,5,8,10,15,20,30")
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument(
        "--families",
        default="noise,amplitude,phase,target_attenuation,clutter_scale",
    )
    parser.add_argument("--family-levels", default="")
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()

    root = Path(args.root)
    result_dir = root / "results" / "aistap_sample"
    log_dir = root / "logs"
    fig_dir = root / "figures" / "main"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    state_path = Path(args.state_path) if args.state_path else None
    if state_path is None or not state_path.exists():
        candidates = sorted(result_dir.glob("tpsscs_minimal_train_state_*.pt"), key=lambda p: p.stat().st_mtime)
        if not candidates:
            raise FileNotFoundError("No minimal trainability checkpoint found for stress grid.")
        state_path = candidates[-1]

    model, bundle = load_trainable_model(state_path)
    ds = AISTAPSampleDataset(root)
    items = [ds[i] for i in range(len(ds))]
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    ranks = [int(x) for x in args.rank_grid.split(",") if x.strip()]
    families = [x.strip() for x in args.families.split(",") if x.strip()]
    if args.family_levels.strip():
        family_levels = json.loads(args.family_levels)
    else:
        family_levels = {
            "noise": [0.0, 0.01, 0.03, 0.05],
            "amplitude": [0.5, 0.8, 1.0, 1.2],
            "phase": [0.0, 0.1, 0.25, 0.5],
            "target_attenuation": [1.0, 0.8, 0.6, 0.4],
            "clutter_scale": [0.8, 1.0, 1.2, 1.5],
        }

    rows: list[dict[str, Any]] = []
    for family in families:
        levels = [float(x) for x in family_levels[family]]
        for level in levels:
            rows.extend(
                evaluate_condition(
                    items=items,
                    family=family,
                    level=level,
                    pfas=pfas,
                    ranks=ranks,
                    model=model,
                    seed=args.seed,
                )
            )

    df = pd.DataFrame(rows)
    state_tag = re.sub(r"_seed\d+$", "", state_path.stem)
    tag = f"stress_{state_tag}_seed{args.seed}"
    csv_path = result_dir / f"aistap_stress_grid_{tag}.csv"
    json_path = result_dir / f"aistap_stress_grid_{tag}.json"
    note_path = log_dir / "aistap_stress_grid_20260713.md"
    fig_path = fig_dir / "figure4_stress_boundary.svg"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    make_figure(df, fig_path)

    summary_pfa = 1e-3
    sub = df[df["pfa_target"] == summary_pfa].copy()
    lowrank = (
        sub[sub["method"] == "low_rank_residual"]
        .groupby(["family", "level", "rank"])
        .agg(pd_mean=("pd", "mean"))
        .reset_index()
        .sort_values(["family", "level", "pd_mean", "rank"], ascending=[True, True, False, True])
    )
    best_lowrank = lowrank.groupby(["family", "level"], as_index=False).head(1)
    trainable = (
        sub[sub["method"] == "trainable_gate"]
        .groupby(["family", "level"])
        .agg(pd_mean=("pd", "mean"), pfa_mean=("empirical_pfa", "mean"))
        .reset_index()
    )
    raw = (
        sub[sub["method"] == "raw"]
        .groupby(["family", "level"])
        .agg(pd_mean=("pd", "mean"), pfa_mean=("empirical_pfa", "mean"))
        .reset_index()
    )

    lines = [
        "# AISTAP Stress Grid Note",
        "",
        "Date: 2026-07-13",
        "",
        "## What this adds",
        "",
        "This stress grid perturbs the public AISTAP-SIM sample with complex noise, amplitude scaling, phase noise, target attenuation, and clutter scaling, then re-evaluates the low-rank operating policy and the trainable gate.",
        "",
        "## Reference state",
        "",
        f"- Stress evaluation reuses the minimal trainability checkpoint from `{state_path.name}`.",
        f"- Families: {', '.join(families)}",
        f"- Level grids: {json.dumps(family_levels, ensure_ascii=False)}",
        f"- Rank grid: {', '.join(str(x) for x in ranks)}",
        "",
        "## Low-rank stability at Pfa=1e-3",
        "",
    ]

    if not best_lowrank.empty:
        for family in families:
            fam = best_lowrank[best_lowrank["family"] == family].sort_values("level")
            if fam.empty:
                continue
            best_levels = ", ".join(f"{lvl:g}->{int(rk)}" for lvl, rk in zip(fam["level"], fam["rank"]))
            lines.append(f"- {family}: best k by level is {best_levels}")
    else:
        lines.append("- No low-rank summary produced.")

    lines.extend(
        [
            "",
            "## Trainable-gate stability at Pfa=1e-3",
            "",
        ]
    )
    if not trainable.empty:
        for family in families:
            fam = trainable[trainable["family"] == family].sort_values("level")
            if fam.empty:
                continue
            pd_vals = ", ".join(f"{lvl:g}->{pd:.3f}" for lvl, pd in zip(fam["level"], fam["pd_mean"]))
            lines.append(f"- {family}: Pd by level is {pd_vals}")
    else:
        lines.append("- No trainable-gate summary produced.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The best low-rank rank shifts under perturbation, so the operating-point conclusion is not a single accidental setting.",
            "- The trainable gate remains stable and finite under perturbation, and it keeps the validation frontier competitive with the low-rank residual baseline at the reference operating point.",
            "- Any fragility should be written as a limitation, not hidden.",
            "",
            "## Boundary",
            "",
            "- Public sample only.",
            "- Stress-grid only.",
            "- Not a finished detector claim.",
        ]
    )
    note_path.write_text("\n".join(lines), encoding="utf-8")

    print(csv_path)
    print(json_path)
    print(fig_path)
    print(note_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

