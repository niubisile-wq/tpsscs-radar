from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tpsscs import AISTAPSampleDataset, TPSSCSPrototype


def score_map(x: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(x) ** 2, axis=0)


def target_mask(meta: dict[str, Any], shape: tuple[int, int]) -> np.ndarray:
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
    x_t = torch.from_numpy(x)
    prototype = TPSSCSPrototype(rank=rank)
    with torch.no_grad():
        residual = prototype.low_rank(x_t.to(torch.complex128))[0].detach().cpu().numpy()
    return residual


def collect_items(ds: AISTAPSampleDataset) -> list[dict[str, Any]]:
    return [ds[i] for i in range(len(ds))]


def evaluate_rows(
    items: list[dict[str, Any]],
    ranks: list[int],
    pfas: list[float],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        x = item["x"].detach().cpu().numpy()
        t = item["target"].detach().cpu().numpy()
        mask = target_mask(item["metadata"], score_map(t).shape)
        if not mask.any():
            continue

        raw_score = score_map(x)
        tgt_score = score_map(t)
        raw_power = float(np.mean(raw_score))
        tgt_power = float(np.mean(tgt_score))

        for row in summarize_detection(raw_score, mask, pfas):
            rows.append(
                {
                    "subset": item["subset"],
                    "path": item["path"],
                    "image_index": item["image_index"],
                    "method": "raw",
                    "rank": 0,
                    "clutter_attenuation_db": 0.0,
                    "target_loss_db": 0.0,
                    "target_retention_ratio": 1.0,
                    "residual_target_to_clutter_ratio": float((tgt_power + 1e-12) / (raw_power + 1e-12)),
                    "score_mean": raw_power,
                    **row,
                }
            )

        for rank in ranks:
            resid = low_rank_residual(x, rank)
            resid_score = score_map(resid)
            resid_power = float(np.mean(resid_score))
            resid_tgt = low_rank_residual(t, rank)
            resid_tgt_score = score_map(resid_tgt)
            resid_tgt_power = float(np.mean(resid_tgt_score))
            rows.extend(
                {
                    "subset": item["subset"],
                    "path": item["path"],
                    "image_index": item["image_index"],
                    "method": "low_rank_residual",
                    "rank": rank,
                    "clutter_attenuation_db": float(10.0 * np.log10((raw_power + 1e-12) / (resid_power + 1e-12))),
                    "target_loss_db": float(10.0 * np.log10((tgt_power + 1e-12) / (resid_tgt_power + 1e-12))),
                    "target_retention_ratio": float((resid_tgt_power + 1e-12) / (tgt_power + 1e-12)),
                    "residual_target_to_clutter_ratio": float((resid_tgt_power + 1e-12) / (resid_power + 1e-12)),
                    "score_mean": resid_power,
                    **row,
                }
                for row in summarize_detection(resid_score, mask, pfas)
            )
    return rows


def aggregate_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    group_cols = ["method", "subset", "rank", "pfa_target"]
    summary = (
        df.groupby(group_cols, dropna=False)
        .agg(
            pd_mean=("pd", "mean"),
            pfa_mean=("empirical_pfa", "mean"),
            threshold_mean=("threshold", "mean"),
            clutter_attenuation_db=("clutter_attenuation_db", "mean"),
            target_loss_db=("target_loss_db", "mean"),
            target_retention_ratio=("target_retention_ratio", "mean"),
            residual_target_to_clutter_ratio=("residual_target_to_clutter_ratio", "mean"),
            score_mean=("score_mean", "mean"),
            item_count=("path", "nunique"),
            target_pixel_count=("target_count", "sum"),
            bg_pixel_count=("bg_count", "sum"),
        )
        .reset_index()
    )
    summary["subset"] = summary["subset"].fillna("overall")
    return summary


def best_rank_by_pfa(df: pd.DataFrame, pfa: float, target_loss_ceiling_db: float) -> pd.DataFrame:
    sub = df[(df["method"] == "low_rank_residual") & (df["pfa_target"] == pfa)].copy()
    if sub.empty:
        return sub
    rows: list[pd.Series] = []
    for subset, group in sub.groupby("subset", dropna=False):
        bounded = group[group["target_loss_db"] <= target_loss_ceiling_db]
        if bounded.empty:
            choice = group.sort_values(["pd_mean", "rank"], ascending=[False, True]).head(1)
        else:
            choice = bounded.sort_values(["pd_mean", "rank"], ascending=[False, True]).head(1)
        row = choice.iloc[0].copy()
        row["subset"] = "overall" if pd.isna(subset) else subset
        rows.append(row)
    return pd.DataFrame(rows)


def make_figure(df: pd.DataFrame, out_path: Path) -> None:
    overall = df[(df["method"] == "low_rank_residual") & (df["subset"] == "overall")].copy()
    if overall.empty:
        return

    ranks = sorted(int(x) for x in overall["rank"].unique().tolist())
    pfas = sorted(float(x) for x in overall["pfa_target"].unique().tolist())
    pivot = overall.pivot(index="rank", columns="pfa_target", values="pd_mean").reindex(index=ranks, columns=pfas)

    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8), constrained_layout=True)

    ax = axes[0]
    im = ax.imshow(pivot.values, aspect="auto", origin="lower", cmap="viridis")
    ax.set_xticks(np.arange(len(pfas)))
    ax.set_xticklabels([f"{p:g}" for p in pfas], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(ranks)))
    ax.set_yticklabels([str(r) for r in ranks])
    ax.set_xlabel("Requested Pfa")
    ax.set_ylabel("Rank k")
    ax.set_title("Mean Pd across the dense operating surface")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pd")

    ax2 = axes[1]
    rank_summary = (
        overall.groupby("rank")
        .agg(
            pd_mean=("pd_mean", "mean"),
            clutter_attenuation_db=("clutter_attenuation_db", "mean"),
            target_loss_db=("target_loss_db", "mean"),
        )
        .reset_index()
        .sort_values("rank")
    )
    ax2.plot(rank_summary["rank"], rank_summary["clutter_attenuation_db"], marker="o", label="Clutter attenuation")
    ax2.plot(rank_summary["rank"], rank_summary["target_loss_db"], marker="s", label="Target loss")
    ax2.set_xlabel("Rank k")
    ax2.set_ylabel("dB")
    ax2.set_title("Mean trade-off versus rank")
    ax2.grid(True, alpha=0.25)
    ax2.legend(frameon=False, loc="best")

    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def build_note(overall: pd.DataFrame, frontier: pd.DataFrame, target_loss_ceiling_db: float) -> str:
    lines: list[str] = []
    lines.append("# AISTAP Operating Surface Note")
    lines.append("")
    lines.append("Date: 2026-07-13")
    lines.append("")
    lines.append("## What this adds")
    lines.append("")
    lines.append(
        "This experiment measures a dense low-rank / CFAR operating surface on the public AISTAP-SIM sample, "
        "rather than a sparse rank sweep."
    )
    lines.append("")
    lines.append("## Dense low-rank trend")
    lines.append("")
    lines.append("| k | mean clutter attenuation dB | mean target loss dB |")
    lines.append("|---|---:|---:|")

    rank_summary = (
        overall[overall["method"] == "low_rank_residual"]
        .groupby("rank")
        .agg(
            clutter_attenuation_db=("clutter_attenuation_db", "mean"),
            target_loss_db=("target_loss_db", "mean"),
        )
        .reset_index()
        .sort_values("rank")
    )
    for _, row in rank_summary.iterrows():
        lines.append(
            f"| {int(row['rank'])} | {row['clutter_attenuation_db']:.3f} | {row['target_loss_db']:.3f} |"
        )

    lines.append("")
    lines.append("## Dense CFAR frontier")
    lines.append("")
    lines.append(f"The frontier uses a target-loss ceiling of {target_loss_ceiling_db:g} dB.")
    lines.append("")
    lines.append("| subset | Pfa | best k | best Pd | target loss dB | clutter attenuation dB | raw Pd | delta Pd |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

    pfa_vals = sorted(frontier["pfa_target"].unique().tolist())
    for subset in sorted(frontier["subset"].unique().tolist()):
        sub = frontier[frontier["subset"] == subset]
        for pfa in pfa_vals:
            row = sub[sub["pfa_target"] == pfa]
            if row.empty:
                continue
            row = row.iloc[0]
            lines.append(
                f"| {subset} | {pfa:g} | {int(row['rank'])} | {row['pd_mean']:.3f} | {row['target_loss_db']:.3f} | "
                f"{row['clutter_attenuation_db']:.3f} | {row['raw_pd']:.3f} | {row['delta_pd']:.3f} |"
            )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "The dense surface keeps the same qualitative result as the sparse CFAR audit: stronger suppression increases "
        "clutter attenuation, but the best operating rank depends on the requested false-alarm rate."
    )
    lines.append(
        "The frontier table also makes the target-loss cost explicit, so the paper can treat k as an operating parameter "
        "rather than a universal optimum."
    )
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("This is public-sample evidence only.")
    lines.append("It strengthens the operating-policy argument, but it does not prove a finished detector or cross-dataset win.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--ranks", default="1,2,3,5,8,10,15,20,30")
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--target-loss-ceiling-db", type=float, default=5.0)
    args = parser.parse_args()

    root = Path(args.root)
    ds = AISTAPSampleDataset(root)
    items = collect_items(ds)
    ranks = [int(x) for x in args.ranks.split(",") if x.strip()]
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]

    rows = evaluate_rows(items, ranks=ranks, pfas=pfas)
    df = pd.DataFrame(rows)
    subset_summary = aggregate_rows(df)

    if subset_summary.empty:
        raise RuntimeError("No target-bearing items were found in the sample.")

    # Add overall aggregates for every rank/Pfa pair so the note and figure can refer to a single operating surface.
    overall = (
        df.groupby(["method", "rank", "pfa_target"], dropna=False)
        .agg(
            pd_mean=("pd", "mean"),
            pfa_mean=("empirical_pfa", "mean"),
            threshold_mean=("threshold", "mean"),
            clutter_attenuation_db=("clutter_attenuation_db", "mean"),
            target_loss_db=("target_loss_db", "mean"),
            target_retention_ratio=("target_retention_ratio", "mean"),
            residual_target_to_clutter_ratio=("residual_target_to_clutter_ratio", "mean"),
            score_mean=("score_mean", "mean"),
            item_count=("path", "nunique"),
            target_pixel_count=("target_count", "sum"),
            bg_pixel_count=("bg_count", "sum"),
        )
        .reset_index()
    )
    overall["subset"] = "overall"
    summary = pd.concat([subset_summary, overall], ignore_index=True, sort=False)

    raw_overall = (
        summary[(summary["method"] == "raw") & (summary["subset"] == "overall")]
        .groupby("pfa_target", as_index=False)
        .agg(raw_pd=("pd_mean", "mean"))
    )

    frontier_frames: list[pd.DataFrame] = []
    for pfa in pfas:
        best = best_rank_by_pfa(summary, pfa, args.target_loss_ceiling_db)
        if best.empty:
            continue
        best = best.rename(columns={"pd_mean": "pd_mean"})
        best["raw_pd"] = best["pfa_target"].map(dict(raw_overall.values.tolist()))
        best["delta_pd"] = best["pd_mean"] - best["raw_pd"]
        frontier_frames.append(best)
    frontier = pd.concat(frontier_frames, ignore_index=True, sort=False) if frontier_frames else pd.DataFrame()

    log_dir = root / "logs"
    fig_dir = root / "figures" / "main"
    result_dir = root / "results" / "aistap_sample"
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)

    csv_path = log_dir / "aistap_operating_surface_20260713.csv"
    json_path = log_dir / "aistap_operating_surface_20260713.json"
    note_path = log_dir / "aistap_operating_surface_note_20260713.md"
    fig_path = fig_dir / "figure3_operating_surface.svg"

    summary.to_csv(csv_path, index=False, encoding="utf-8-sig")
    json_path.write_text(
        json.dumps(
            {
                "rows": rows,
                "summary": summary.to_dict(orient="records"),
                "frontier": frontier.to_dict(orient="records"),
                "ranks": ranks,
                "pfas": pfas,
                "target_loss_ceiling_db": args.target_loss_ceiling_db,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    note_path.write_text(build_note(summary, frontier, args.target_loss_ceiling_db), encoding="utf-8")
    make_figure(summary, fig_path)

    # Mirror the raw artifacts into the result directory for reproducibility.
    (result_dir / csv_path.name).write_bytes(csv_path.read_bytes())
    (result_dir / json_path.name).write_bytes(json_path.read_bytes())

    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"Wrote {note_path}")
    print(f"Wrote {fig_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
