from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures" / "main"
LOG_DIR = ROOT / "logs"
DATE = "20260715"

COLORS = {
    "tpsscs": "#2F6F73",
    "raw": "#5F6670",
    "lowrank": "#B16A3B",
    "fusion": "#2F6F73",
    "candidate": "#2F6F73",
    "accent": "#C2473B",
    "grid": "#D6D9DD",
    "zero": "#222222",
    "fill": "#DDECEE",
    "lowfill": "#F2E4D8",
}

METHOD_LABELS = {
    "tpsscs_finished_detector": "TP-SSCS",
    "raw": "Raw",
    "low_rank_residual_k30": "Low-rank",
    "ipix_validated_residual_fusion": "Residual-aware fusion",
}

PFA_LABELS = {
    1e-5: "1e-5",
    3e-5: "3e-5",
    1e-4: "1e-4",
    3e-4: "3e-4",
    1e-3: "1e-3",
    3e-3: "3e-3",
    1e-2: "1e-2",
}


def setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 6.5,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.7,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "figure.dpi": 150,
        }
    )


def save_figure(fig: mpl.figure.Figure, stem: str, fig_dir: Path = FIG_DIR) -> list[str]:
    fig_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[str] = []
    for ext, kwargs in [
        ("svg", {}),
        ("pdf", {}),
        ("png", {"dpi": 600}),
    ]:
        path = fig_dir / f"{stem}.{ext}"
        fig.savefig(path, bbox_inches="tight", **kwargs)
        outputs.append(str(path.relative_to(ROOT)))
    return outputs


def panel_label(ax: mpl.axes.Axes, label: str) -> None:
    ax.text(
        -0.12,
        1.08,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        fontweight="bold",
    )


def as_float(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        out[col] = out[col].astype(float)
    return out


def pfa_ticks(ax: mpl.axes.Axes) -> None:
    ticks = np.array([1e-5, 1e-4, 1e-3, 1e-2])
    ax.set_xscale("log")
    ax.set_xticks(ticks)
    ax.set_xticklabels([PFA_LABELS[float(t)] for t in ticks])


def format_pfa_all(values: Iterable[float]) -> list[str]:
    return [PFA_LABELS.get(float(v), f"{float(v):.0e}") for v in values]


def draw_delta_ci(ax: mpl.axes.Axes, ci: pd.DataFrame, comparator_order: list[str], title: str) -> None:
    markers = {"raw": "o", "low_rank_residual_k30": "s", "lowrank": "s"}
    colors = {"raw": COLORS["raw"], "low_rank_residual_k30": COLORS["lowrank"], "lowrank": COLORS["lowrank"]}
    labels = {"raw": "vs Raw", "low_rank_residual_k30": "vs Low-rank", "lowrank": "vs Low-rank"}
    for comparator in comparator_order:
        sub = ci[ci["comparator"] == comparator].sort_values("pfa")
        if sub.empty:
            continue
        x = sub["pfa"].to_numpy(float)
        y = sub["mean_delta_pd"].to_numpy(float)
        lo = sub["ci95_low"].to_numpy(float)
        hi = sub["ci95_high"].to_numpy(float)
        ax.fill_between(x, lo, hi, color=colors[comparator], alpha=0.18, lw=0)
        ax.plot(
            x,
            y,
            marker=markers[comparator],
            ms=3.2,
            lw=1.4,
            color=colors[comparator],
            label=labels[comparator],
        )
    ax.axhline(0, color=COLORS["zero"], lw=0.7, ls="--")
    pfa_ticks(ax)
    ax.set_ylabel("Delta Pd")
    ax.set_xlabel("Target Pfa")
    ax.set_title(title, loc="left", pad=3)
    ax.grid(axis="y", color=COLORS["grid"], lw=0.5, alpha=0.8)
    ax.legend(loc="best")


def figure4(
    stem: str = f"figure4_official_full_asset_validation_{DATE}",
    include_suptitle: bool = True,
    fig_dir: Path = FIG_DIR,
) -> list[str]:
    protocol = as_float(
        pd.read_csv(ROOT / "results" / "aistap_full_asset" / f"aistap_combined_full_asset_protocol_{DATE}.csv"),
        [
            "pfa",
            "target_pd",
            "raw_pd",
            "lowrank_pd",
            "delta_vs_raw",
            "delta_vs_lowrank",
            "target_empirical_pfa",
            "pfa_ceiling",
        ],
    )
    ci = as_float(
        pd.read_csv(ROOT / "results" / "aistap_full_asset" / f"aistap_combined_full_asset_bootstrap_ci_{DATE}.csv"),
        ["pfa", "mean_delta_pd", "ci95_low", "ci95_high", "positive_fraction"],
    )
    combined = protocol[protocol["asset"] == "combined"].sort_values("pfa")
    assets = protocol[protocol["asset"].isin(["simMed_test.mat", "simWind_test.mat"])]

    fig = plt.figure(figsize=(7.2, 5.3))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.18, 1], height_ratios=[1, 0.92], wspace=0.38, hspace=0.45)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    panel_label(ax_a, "a")
    ax_a.plot(combined["pfa"], combined["target_pd"], marker="o", color=COLORS["tpsscs"], lw=1.8, ms=3.5, label="TP-SSCS")
    ax_a.plot(combined["pfa"], combined["raw_pd"], marker="o", color=COLORS["raw"], lw=1.3, ms=3.2, label="Raw")
    ax_a.plot(combined["pfa"], combined["lowrank_pd"], marker="o", color=COLORS["lowrank"], lw=1.3, ms=3.2, label="Low-rank")
    pfa_ticks(ax_a)
    ax_a.set_ylim(0, 0.95)
    ax_a.set_xlabel("Target Pfa")
    ax_a.set_ylabel("Detection probability (Pd)")
    ax_a.set_title("Official full-asset detector curve", loc="left", pad=3)
    ax_a.grid(axis="y", color=COLORS["grid"], lw=0.5, alpha=0.8)
    ax_a.legend(loc="lower right")
    ax_a.text(
        0.03,
        0.93,
        "210 target-bearing frames\n7/7 combined wins",
        transform=ax_a.transAxes,
        ha="left",
        va="top",
        fontsize=6.5,
        bbox={"facecolor": "white", "edgecolor": COLORS["grid"], "boxstyle": "round,pad=0.25"},
    )

    panel_label(ax_b, "b")
    draw_delta_ci(ax_b, ci, ["raw", "low_rank_residual_k30"], "Paired bootstrap support")

    panel_label(ax_c, "c")
    heat_rows = []
    row_labels = []
    for asset_name, label in [("simMed_test.mat", "simMed vs Raw"), ("simWind_test.mat", "simWind vs Raw")]:
        sub = assets[assets["asset"] == asset_name].sort_values("pfa")
        heat_rows.append(sub["delta_vs_raw"].to_numpy(float))
        row_labels.append(label)
    for asset_name, label in [("simMed_test.mat", "simMed vs Low-rank"), ("simWind_test.mat", "simWind vs Low-rank")]:
        sub = assets[assets["asset"] == asset_name].sort_values("pfa")
        heat_rows.append(sub["delta_vs_lowrank"].to_numpy(float))
        row_labels.append(label)
    heat = np.vstack(heat_rows)
    heat_vmax = max(0.35, np.nanmax(heat))
    heat_cmap = plt.get_cmap("YlOrBr")
    im = ax_c.imshow(heat, aspect="auto", cmap=heat_cmap, vmin=0, vmax=heat_vmax)
    ax_c.set_yticks(np.arange(len(row_labels)))
    ax_c.set_yticklabels(row_labels)
    pfas = assets[assets["asset"] == "simMed_test.mat"].sort_values("pfa")["pfa"].to_numpy(float)
    ax_c.set_xticks(np.arange(len(pfas)))
    ax_c.set_xticklabels(format_pfa_all(pfas), rotation=45, ha="right")
    ax_c.set_title("Asset-level delta Pd remains positive", loc="left", pad=3)
    ax_c.set_xlabel("Target Pfa")
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            norm_value = np.clip(heat[i, j] / heat_vmax, 0, 1)
            r, g, b, _ = heat_cmap(norm_value)
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            text_color = "#111111" if luminance > 0.58 else "#FFFFFF"
            ax_c.text(j, i, f"{heat[i, j]:.02f}", ha="center", va="center", fontsize=5.8, color=text_color)
    cb = fig.colorbar(im, ax=ax_c, fraction=0.034, pad=0.02)
    cb.set_label("Delta Pd", fontsize=6)
    cb.ax.tick_params(labelsize=5.5)

    panel_label(ax_d, "d")
    ax_d.plot([1e-5, 1e-2], [1e-5, 1e-2], color=COLORS["raw"], lw=0.9, ls=":", label="Requested Pfa")
    ax_d.plot(combined["pfa"], combined["pfa_ceiling"], color=COLORS["lowrank"], lw=1.0, ls="--", label="Protocol ceiling")
    ax_d.scatter(combined["pfa"], combined["target_empirical_pfa"], s=22, color=COLORS["tpsscs"], zorder=3, label="Observed TP-SSCS")
    ax_d.set_xscale("log")
    ax_d.set_yscale("log")
    ax_d.set_xlim(7e-6, 1.5e-2)
    ax_d.set_ylim(5e-7, 1.5e-2)
    ax_d.set_xlabel("Target Pfa")
    ax_d.set_ylabel("Empirical Pfa")
    ax_d.set_title("False-alarm calibration", loc="left", pad=3)
    ax_d.grid(which="both", color=COLORS["grid"], lw=0.45, alpha=0.75)
    ax_d.legend(loc="lower right")
    if include_suptitle:
        fig.suptitle("Figure 4 | Official AISTAP-SIM full-asset detector validation", x=0.02, y=0.995, ha="left", fontsize=10, fontweight="bold")
    return save_figure(fig, stem, fig_dir)


def load_ipix_summary() -> pd.DataFrame:
    df = as_float(
        pd.read_csv(ROOT / "results" / "ipix_external" / f"ipix_validated_residual_fusion_test_{DATE}.csv"),
        ["pfa_target", "pd"],
    )
    summary = (
        df[df["method"].isin(["raw", "low_rank_residual_k30", "ipix_validated_residual_fusion"])]
        .groupby(["method", "pfa_target"], as_index=False)["pd"]
        .mean()
        .rename(columns={"pfa_target": "pfa"})
    )
    return summary


def figure5(
    stem: str = f"figure5_external_radar_validation_{DATE}",
    include_suptitle: bool = True,
    fig_dir: Path = FIG_DIR,
) -> list[str]:
    ipix = load_ipix_summary()
    ipix_ci = as_float(
        pd.read_csv(ROOT / "results" / "aistap_supplementary" / f"ipix_heldout_bootstrap_delta_ci_{DATE}.csv"),
        ["pfa", "mean_delta_pd", "ci95_low", "ci95_high", "positive_unit_fraction"],
    )
    ssdd_curve = as_float(
        pd.read_csv(ROOT / "results" / "ssdd_external" / f"ssdd_external_trainable_gate_{DATE}.csv"),
        ["pfa", "candidate_pd", "raw_pd", "lowrank_pd", "candidate_empirical_pfa"],
    )
    ssdd_ci = as_float(
        pd.read_csv(ROOT / "results" / "ssdd_external" / f"ssdd_image_annotation_bootstrap_ci_{DATE}.csv"),
        ["pfa", "mean_delta_pd", "ci95_low", "ci95_high", "positive_fraction"],
    )
    zero_json = json.loads(
        (ROOT / "results" / "ipix_external" / f"ipix_external_detector_transfer_19931107_135603_starea_{DATE}.json").read_text(
            encoding="utf-8"
        )
    )
    zero_comp = {float(row["pfa"]): row for row in zero_json.get("comparisons", [])}
    z1e2 = zero_comp.get(1e-2, {})

    fig = plt.figure(figsize=(7.2, 5.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1], height_ratios=[1, 1], wspace=0.36, hspace=0.46)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    panel_label(ax_a, "a")
    for method, color, marker in [
        ("ipix_validated_residual_fusion", COLORS["fusion"], "o"),
        ("raw", COLORS["raw"], "o"),
        ("low_rank_residual_k30", COLORS["lowrank"], "o"),
    ]:
        sub = ipix[ipix["method"] == method].sort_values("pfa")
        ax_a.plot(sub["pfa"], sub["pd"], marker=marker, ms=3.2, lw=1.5, color=color, label=METHOD_LABELS[method])
    pfa_ticks(ax_a)
    ax_a.set_ylim(0, 0.16)
    ax_a.set_xlabel("Target Pfa")
    ax_a.set_ylabel("Held-out Pd")
    ax_a.set_title("IPIX held-out fusion", loc="left", pad=3)
    ax_a.grid(axis="y", color=COLORS["grid"], lw=0.5, alpha=0.8)
    ax_a.legend(loc="upper left")
    if z1e2:
        ax_a.text(
            0.98,
            0.08,
            f"Zero-shot boundary at 1e-2:\nraw {z1e2.get('raw_pd', 0):.3f} > TP-SSCS {z1e2.get('tpsscs_pd', 0):.3f}",
            transform=ax_a.transAxes,
            ha="right",
            va="bottom",
            fontsize=6.2,
            bbox={"facecolor": "white", "edgecolor": COLORS["grid"], "boxstyle": "round,pad=0.25"},
        )

    panel_label(ax_b, "b")
    draw_delta_ci(ax_b, ipix_ci, ["raw", "low_rank_residual_k30"], "IPIX recording-level delta")

    panel_label(ax_c, "c")
    ax_c.plot(ssdd_curve["pfa"], ssdd_curve["candidate_pd"], marker="o", color=COLORS["candidate"], lw=1.7, ms=3.2, label="Candidate")
    ax_c.plot(ssdd_curve["pfa"], ssdd_curve["raw_pd"], marker="o", color=COLORS["raw"], lw=1.3, ms=3.2, label="Raw")
    ax_c.plot(ssdd_curve["pfa"], ssdd_curve["lowrank_pd"], marker="o", color=COLORS["lowrank"], lw=1.3, ms=3.2, label="Low-rank")
    pfa_ticks(ax_c)
    ax_c.set_ylim(0, 0.82)
    ax_c.set_xlabel("Target Pfa")
    ax_c.set_ylabel("Official-test Pd")
    ax_c.set_title("SSDD supervised SAR adaptation", loc="left", pad=3)
    ax_c.grid(axis="y", color=COLORS["grid"], lw=0.5, alpha=0.8)
    ax_c.legend(loc="upper left")
    ax_c.text(
        0.97,
        0.08,
        "231 images, 545 annotations\n4 wins + 3 ties vs raw",
        transform=ax_c.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.3,
        bbox={"facecolor": "white", "edgecolor": COLORS["grid"], "boxstyle": "round,pad=0.25"},
    )

    panel_label(ax_d, "d")
    image_ci = ssdd_ci[ssdd_ci["level"] == "image"].copy()
    draw_delta_ci(ax_d, image_ci, ["raw", "lowrank"], "SSDD image-level delta")
    ax_d.text(
        0.03,
        0.93,
        "Raw fallback ties at Pfa <= 1e-4",
        transform=ax_d.transAxes,
        ha="left",
        va="top",
        fontsize=6.2,
        bbox={"facecolor": "white", "edgecolor": COLORS["grid"], "boxstyle": "round,pad=0.25"},
    )
    if include_suptitle:
        fig.suptitle("Figure 5 | Bounded external radar-family validation", x=0.02, y=0.995, ha="left", fontsize=10, fontweight="bold")
    return save_figure(fig, stem, fig_dir)


def boxplot_deltas(ax: mpl.axes.Axes, df: pd.DataFrame, pfas: list[float], col: str, title: str, color: str) -> None:
    data = [df[np.isclose(df["pfa"], pfa)][col].dropna().to_numpy(float) for pfa in pfas]
    positions = np.arange(len(pfas))
    bp = ax.boxplot(
        data,
        positions=positions,
        widths=0.55,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#1A1A1A", "linewidth": 1.0},
        whiskerprops={"color": "#5A5A5A", "linewidth": 0.8},
        capprops={"color": "#5A5A5A", "linewidth": 0.8},
    )
    for patch in bp["boxes"]:
        patch.set_facecolor(color)
        patch.set_alpha(0.45)
        patch.set_edgecolor("#555555")
        patch.set_linewidth(0.8)
    means = [float(np.mean(x)) if len(x) else np.nan for x in data]
    ax.scatter(positions, means, s=16, color=color, edgecolor="#222222", linewidth=0.35, zorder=3, label="Mean")
    ax.axhline(0, color=COLORS["zero"], lw=0.7, ls="--")
    ax.set_xticks(positions)
    ax.set_xticklabels(format_pfa_all(pfas), rotation=45, ha="right")
    ax.set_title(title, loc="left", pad=3)
    ax.set_ylabel("Delta Pd")
    ax.grid(axis="y", color=COLORS["grid"], lw=0.5, alpha=0.8)


def extended_data_figure1(
    stem: str = f"extended_data_figure1_ssdd_robustness_{DATE}",
    include_suptitle: bool = True,
    fig_dir: Path = FIG_DIR,
) -> list[str]:
    image = as_float(
        pd.read_csv(ROOT / "results" / "ssdd_external" / f"ssdd_image_level_robustness_{DATE}.csv"),
        ["pfa", "delta_vs_raw", "delta_vs_lowrank"],
    )
    annotation = as_float(
        pd.read_csv(ROOT / "results" / "ssdd_external" / f"ssdd_annotation_level_robustness_{DATE}.csv"),
        ["pfa", "delta_vs_raw", "delta_vs_lowrank"],
    )
    raw_pfas = [3e-4, 1e-3, 3e-3, 1e-2]
    all_pfas = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2]

    fig = plt.figure(figsize=(7.2, 5.2))
    gs = fig.add_gridspec(2, 2, wspace=0.35, hspace=0.52)
    axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]

    panel_label(axes[0], "a")
    boxplot_deltas(axes[0], image, raw_pfas, "delta_vs_raw", "Image-level gains vs raw", COLORS["tpsscs"])
    axes[0].set_ylim(-0.55, 1.05)

    panel_label(axes[1], "b")
    boxplot_deltas(axes[1], annotation, raw_pfas, "delta_vs_raw", "Annotation-level gains vs raw", COLORS["tpsscs"])
    axes[1].set_ylim(-0.55, 1.05)

    panel_label(axes[2], "c")
    boxplot_deltas(axes[2], image, all_pfas, "delta_vs_lowrank", "Image-level gains vs low-rank", COLORS["lowrank"])
    axes[2].set_ylim(-0.35, 1.15)

    panel_label(axes[3], "d")
    boxplot_deltas(axes[3], annotation, all_pfas, "delta_vs_lowrank", "Annotation-level gains vs low-rank", COLORS["lowrank"])
    axes[3].set_ylim(-0.35, 1.15)

    for ax in axes:
        ax.set_xlabel("Target Pfa")
    if include_suptitle:
        fig.suptitle(
            "Extended Data Figure 1 | SSDD image- and annotation-level robustness",
            x=0.02,
            y=0.995,
            ha="left",
            fontsize=10,
            fontweight="bold",
        )
    return save_figure(fig, stem, fig_dir)


def write_log(outputs: dict[str, list[str]]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"aistap_submission_figures_20260715.md"
    lines = [
        "# AISTAP Submission Figure Generation",
        "",
        f"Date: {DATE}",
        "",
        "## Figure Contract",
        "",
        "- Figure 4 conclusion: the official AISTAP-SIM full-asset detector gate passes with calibrated Pfa and positive paired bootstrap support.",
        "- Figure 5 conclusion: IPIX and SSDD provide bounded external radar-family support, with explicit zero-shot and supervised-adaptation boundaries.",
        "- Extended Data Figure 1 conclusion: SSDD gains are visible at image and annotation levels, not only in pooled-pixel aggregates.",
        "",
        "## Outputs",
        "",
    ]
    for name, paths in outputs.items():
        lines.append(f"### {name}")
        for path in paths:
            lines.append(f"- `{path}`")
        lines.append("")
    lines.extend(
        [
            "## Draft Figure Legends",
            "",
            "### Figure 4 | Official AISTAP-SIM full-asset detector validation",
            "",
            "a, Combined detector operating curves over `simMed_test.mat` and `simWind_test.mat` show TP-SSCS, raw maps, and rank-matched low-rank residuals across seven target Pfa values. b, Paired bootstrap confidence intervals over 210 target-bearing frames show positive mean delta Pd for TP-SSCS versus both comparators. c, Asset-level heatmap shows positive delta Pd on both official full-test assets and against both comparator families. d, Empirical Pfa remains within the protocol ceiling across the combined full-asset operating points.",
            "",
            "### Figure 5 | Bounded external radar-family validation",
            "",
            "a, IPIX held-out recordings show validation-selected residual-aware fusion against raw and low-rank residual baselines; direct zero-shot transfer is retained as a negative boundary. b, Recording-level bootstrap confidence intervals show positive mean delta Pd for the IPIX fusion policy. c, SSDD official-test SAR ship imagery shows supervised trainable-gate adaptation against raw and low-rank baselines. d, SSDD image-level bootstrap confidence intervals show no-regression raw fallback at extreme low Pfa and positive non-fallback gains.",
            "",
            "### Extended Data Figure 1 | SSDD image- and annotation-level robustness",
            "",
            "Image-level and annotation-level boxplots show the distribution of SSDD detection-probability gains against raw at non-fallback Pfa points and against low-rank residuals across all Pfa points. Box centres show medians, boxes show interquartile ranges, whiskers exclude plotted outliers, and filled circles mark means.",
            "",
            "## Source Data",
            "",
            "- `results/aistap_full_asset/aistap_combined_full_asset_protocol_20260715.csv`",
            "- `results/aistap_full_asset/aistap_combined_full_asset_bootstrap_ci_20260715.csv`",
            "- `results/ipix_external/ipix_validated_residual_fusion_test_20260715.csv`",
            "- `results/aistap_supplementary/ipix_heldout_bootstrap_delta_ci_20260715.csv`",
            "- `results/ssdd_external/ssdd_external_trainable_gate_20260715.csv`",
            "- `results/ssdd_external/ssdd_image_annotation_bootstrap_ci_20260715.csv`",
            "- `results/ssdd_external/ssdd_image_level_robustness_20260715.csv`",
            "- `results/ssdd_external/ssdd_annotation_level_robustness_20260715.csv`",
            "",
            "## Boundary",
            "",
            "- IPIX zero-shot transfer remains negative and is annotated as a boundary.",
            "- SSDD is supervised external adaptation, not zero-shot saved-state transfer.",
            "- The figures visualize existing result artifacts only; no synthetic data are generated.",
        ]
    )
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path


def main() -> int:
    setup_style()
    outputs = {
        "Figure 4": figure4(),
        "Figure 5": figure5(),
        "Extended Data Figure 1": extended_data_figure1(),
    }
    log_path = write_log(outputs)
    print(log_path.relative_to(ROOT))
    for paths in outputs.values():
        for path in paths:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
