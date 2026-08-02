from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "figure_data"
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update(
    {
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 7.0,
        "axes.labelsize": 7.0,
        "axes.titlesize": 7.6,
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 6.5,
        "legend.fontsize": 6.4,
        "axes.linewidth": 0.75,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "figure.dpi": 200,
    }
)

INK = "#1F2937"
MUTED = "#667085"
GRID = "#E4E8EE"
RAW = "#9AA5B1"
RES = "#4676A9"
TP = "#4F9856"
GOLD = "#D99A28"
RED = "#C84B4B"
PALE_BLUE = "#EAF1F8"
PALE_GREEN = "#EAF5EA"
PALE_GOLD = "#FAF2DF"
PALE_GRAY = "#F1F3F6"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def save_all(fig: mpl.figure.Figure, stem: str) -> None:
    kwargs = {"bbox_inches": "tight", "pad_inches": 0.025, "facecolor": "white"}
    fig.savefig(OUT / f"{stem}.svg", **kwargs)
    fig.savefig(OUT / f"{stem}.pdf", **kwargs)
    fig.savefig(OUT / f"{stem}.tiff", dpi=600, **kwargs)
    fig.savefig(OUT / f"{stem}.png", dpi=300, **kwargs)
    plt.close(fig)


def panel_label(ax: mpl.axes.Axes, label: str, x: float = -0.13, y: float = 1.02) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.0,
        fontweight="bold",
        color=INK,
        clip_on=False,
    )


def style_axis(ax: mpl.axes.Axes, grid_axis: str = "both") -> None:
    ax.grid(True, axis=grid_axis, color=GRID, linewidth=0.65)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.8, width=0.75, colors=INK)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)


def rounded_box(
    ax: mpl.axes.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    facecolor: str,
    edgecolor: str,
    fontsize: float = 6.8,
    linewidth: float = 1.0,
) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.025",
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=linewidth,
        )
    )
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=INK,
        linespacing=1.12,
    )


def arrow(
    ax: mpl.axes.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str,
    connectionstyle: str = "arc3,rad=0",
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=8,
            linewidth=1.15,
            color=color,
            connectionstyle=connectionstyle,
            shrinkA=1,
            shrinkB=1,
        )
    )


def make_fig1() -> None:
    fig, ax = plt.subplots(figsize=(3.50, 4.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    rounded_box(ax, 0.29, 0.875, 0.42, 0.075, "Complex radar frame  $X$", PALE_GRAY, INK, 7.2)

    rounded_box(ax, 0.05, 0.695, 0.39, 0.105, "Rank-$k$ decomposition\nresidual  $R_k$", PALE_BLUE, RES)
    rounded_box(ax, 0.56, 0.695, 0.39, 0.105, "Raw statistic\n$S_{\\mathrm{raw}}=\\sum_c |X_c|^2$", PALE_GREEN, TP)
    arrow(ax, (0.42, 0.875), (0.25, 0.80), RES)
    arrow(ax, (0.58, 0.875), (0.75, 0.80), TP)

    rounded_box(ax, 0.05, 0.505, 0.39, 0.105, "Residual statistic\n$S_{\\mathrm{res}}=\\sum_c |R_{k,c}|^2$", PALE_BLUE, RES)
    rounded_box(
        ax,
        0.56,
        0.505,
        0.39,
        0.105,
        "Compact gate\n$S_{\\mathrm{gate}}=g_\\phi(\\ell_{\\mathrm{raw}},\\ell_{\\mathrm{res}})$\n"
        "$\\ell_\\bullet=\\log(1+S_\\bullet)$",
        PALE_GREEN,
        TP,
        5.9,
    )
    arrow(ax, (0.245, 0.695), (0.245, 0.61), RES)
    arrow(ax, (0.44, 0.557), (0.56, 0.557), TP)
    arrow(ax, (0.755, 0.695), (0.755, 0.61), TP)

    ax.text(
        0.5,
        0.455,
        "two score maps; evaluation readout declared separately",
        ha="center",
        va="center",
        fontsize=5.9,
        color=MUTED,
    )

    rounded_box(
        ax,
        0.08,
        0.245,
        0.84,
        0.125,
        "PRIMARY: target-blind alarm budget\n"
        "within-frame ranks  $Q_{\\mathrm{res}},Q_{\\mathrm{gate}}$;  "
        "$Q_{\\mathrm{TP}}=\\max(Q_{\\mathrm{res}},Q_{\\mathrm{gate}})$\n"
        "select the common top-$K_\\alpha$ cells",
        PALE_GOLD,
        GOLD,
        6.3,
        1.1,
    )
    arrow(ax, (0.245, 0.505), (0.37, 0.37), RES)
    arrow(ax, (0.755, 0.505), (0.63, 0.37), TP)

    rounded_box(
        ax,
        0.12,
        0.055,
        0.76,
        0.095,
        "DIAGNOSTIC ONLY: mask-assisted branch union\n"
        "$S_{\\mathrm{res}}>\\tau_{\\mathrm{res},\\alpha}$  OR  "
        "$S_{\\mathrm{gate}}>\\tau_{\\mathrm{gate},0}$",
        PALE_GRAY,
        MUTED,
        6.1,
        0.9,
    )
    ax.text(0.5, 0.188, "alternative readout of the same score maps", ha="center", va="center", fontsize=5.7, color=MUTED)

    ax.text(0.245, 0.665, "background-tail control", ha="center", va="top", fontsize=6.0, color=RES)
    ax.text(0.755, 0.665, "target-preserving route", ha="center", va="top", fontsize=6.0, color=TP)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
    save_all(fig, "fig1_tp_sscs_policy_singlecol")


def make_fig2() -> None:
    rows = read_csv("fig2_mechanism.csv")
    datasets = ["simMed", "simWind", "simNoiseOnly"]
    fig, axes = plt.subplots(3, 1, figsize=(3.50, 4.35), sharex=True, sharey=True)

    for idx, (ax, dataset) in enumerate(zip(axes, datasets)):
        selected = [row for row in rows if row["dataset"] == dataset]
        k = np.array([float(row["k"]) for row in selected])
        attenuation = np.array([float(row["clutter_attenuation_db"]) for row in selected])
        loss = np.array([float(row["target_loss_db"]) for row in selected])
        ax.plot(k, attenuation, color=RES, lw=1.7, marker="o", ms=4.0, label="Clutter attenuation")
        ax.plot(k, loss, color=GOLD, lw=1.7, marker="s", ms=3.8, label="Target loss")
        ax.set_title(dataset, loc="left", pad=2.5, fontweight="bold")
        ax.set_ylim(0, 21.5)
        ax.set_yticks([0, 5, 10, 15, 20])
        ax.set_xticks([1, 20, 30])
        style_axis(ax)
        panel_label(ax, chr(ord("a") + idx), x=-0.14, y=1.00)

    axes[1].set_ylabel("Level (dB)")
    axes[-1].set_xlabel("Retained rank  $k$")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.54, 0.995), ncol=2, handlelength=1.8)
    fig.subplots_adjust(left=0.19, right=0.98, top=0.91, bottom=0.10, hspace=0.34)
    save_all(fig, "fig2_mechanism_audit_singlecol")


def make_fig3() -> None:
    rows = read_csv("fig3_ablation.csv")
    methods = [row["method"] for row in rows]
    values = np.array([float(row["pd_at_1e_5"]) for row in rows])

    fig = plt.figure(figsize=(3.50, 4.35))
    gs = fig.add_gridspec(2, 1, height_ratios=[3.1, 1.0], hspace=0.48)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    y = np.arange(len(methods))
    colors = [TP, RES] + ["#D8DEE7"] * (len(methods) - 2)
    bars = ax_a.barh(y, values, color=colors, edgecolor="white", height=0.62)
    ax_a.invert_yaxis()
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(methods)
    ax_a.set_xlim(0, 0.205)
    ax_a.set_xticks([0, 0.05, 0.10, 0.15, 0.20])
    ax_a.set_xlabel(r"$P_{\mathrm{D}}$ at $P_{\mathrm{FA}}=10^{-5}$")
    style_axis(ax_a, "x")
    panel_label(ax_a, "a")
    ax_a.set_title("Strict-tail rescue ablation", loc="left", pad=4, fontweight="bold")
    for bar, value in zip(bars, values):
        ax_a.text(value + 0.003, bar.get_y() + bar.get_height() / 2, f"{value:.4f}", ha="left", va="center", fontsize=6.1, color=INK)

    auc_names = ["TP-SSCS", "Residual-heavy fixed mixture"]
    auc_values = [0.5313, 0.5378]
    auc_y = np.array([1, 0])
    ax_b.hlines(auc_y, 0.528, auc_values, color=GRID, lw=2.2)
    ax_b.scatter(auc_values, auc_y, s=34, color=[TP, GOLD], zorder=3)
    ax_b.set_yticks(auc_y)
    ax_b.set_yticklabels(auc_names)
    ax_b.set_xlim(0.528, 0.541)
    ax_b.set_xticks([0.530, 0.535, 0.540])
    ax_b.set_xlabel("Seven-point checked-grid AUC")
    style_axis(ax_b, "x")
    panel_label(ax_b, "b")
    for x, y0 in zip(auc_values, auc_y):
        ax_b.text(x + 0.00035, y0, f"{x:.4f}", ha="left", va="center", fontsize=6.2, color=INK)
    ax_b.set_ylim(-0.55, 1.55)

    fig.subplots_adjust(left=0.39, right=0.97, top=0.96, bottom=0.10)
    save_all(fig, "fig3_rescue_ablation_singlecol")


def make_fig4() -> None:
    rows = read_csv("fig4_main_validation.csv")
    pfa = np.array([float(row["pfa"]) for row in rows])
    raw = np.array([float(row["raw_pd"]) for row in rows])
    residual = np.array([float(row["residual_pd"]) for row in rows])
    tpsscs = np.array([float(row["tpsscs_pd"]) for row in rows])

    fig, ax = plt.subplots(figsize=(3.50, 3.05))
    ax.plot(pfa, raw, color=RAW, lw=1.55, marker="o", ms=3.8, label="Raw")
    ax.plot(pfa, residual, color=RES, lw=1.65, marker="s", ms=3.6, label="Rank-30 residual")
    ax.plot(pfa, tpsscs, color=TP, lw=1.95, marker="^", ms=4.2, label="TP-SSCS")
    ax.fill_between(pfa, residual, tpsscs, color=TP, alpha=0.09, linewidth=0)
    ax.set_xscale("log")
    ax.set_xlim(7e-6, 1.4e-2)
    ax.set_ylim(0, 0.94)
    ax.set_xticks([1e-5, 1e-4, 1e-3, 1e-2])
    ax.set_xticklabels([r"$10^{-5}$", r"$10^{-4}$", r"$10^{-3}$", r"$10^{-2}$"])
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
    ax.set_xlabel(r"Target $P_{\mathrm{FA}}$")
    ax.set_ylabel(r"$P_{\mathrm{D}}$")
    style_axis(ax)
    ax.legend(loc="upper left", ncol=1, handlelength=1.6)
    ax.axvspan(7e-6, 1.1e-4, color=GOLD, alpha=0.055, zorder=-2)
    ax.text(1.25e-5, 0.885, "strict tail", fontsize=6.0, color=GOLD, ha="left", va="top")

    for value, color, dy in [(raw[0], RAW, -7), (residual[0], RES, 6), (tpsscs[0], TP, 15)]:
        ax.annotate(f"{value:.4f}", (pfa[0], value), xytext=(8, dy), textcoords="offset points", fontsize=5.9, color=color, ha="left", va="center")
    ax.annotate(
        r"$\Delta P_{\mathrm{D}}=0.0831$",
        xy=(1e-5, tpsscs[0]),
        xytext=(4.2e-5, 0.31),
        fontsize=6.2,
        color=TP,
        arrowprops={"arrowstyle": "->", "color": TP, "lw": 0.75},
        ha="left",
    )
    fig.subplots_adjust(left=0.17, right=0.98, top=0.97, bottom=0.17)
    save_all(fig, "fig4_main_validation_singlecol")


def make_fig5() -> None:
    ipix_rows = read_csv("fig5_ipix.csv")
    ssdd_rows = read_csv("fig5_ssdd.csv")

    fig = plt.figure(figsize=(3.50, 4.65))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.12], hspace=0.55)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    raw_ipix = np.array([float(row["raw_pd"]) for row in ipix_rows])
    adapted_ipix = np.array([float(row["adapted_pd"]) for row in ipix_rows])
    x = np.arange(len(ipix_rows))
    width = 0.34
    bars_raw = ax_a.bar(x - width / 2, raw_ipix, width, color=RAW, label="Raw")
    bars_adapted = ax_a.bar(x + width / 2, adapted_ipix, width, color=RES, label="Adapted")
    ax_a.set_xticks(x)
    ax_a.set_xticklabels([r"$10^{-5}$", r"$10^{-4}$"])
    ax_a.set_ylim(0.045, 0.077)
    ax_a.set_yticks([0.05, 0.06, 0.07])
    ax_a.set_ylabel(r"$P_{\mathrm{D}}$")
    style_axis(ax_a, "y")
    ax_a.legend(loc="upper left", ncol=2, handlelength=1.2)
    panel_label(ax_a, "a")
    ax_a.set_title("IPIX: adaptation after negative zero-shot transfer", loc="left", pad=4, fontweight="bold")
    ax_a.text(0.98, 0.96, "selection: 1 recording; test: 12", transform=ax_a.transAxes, ha="right", va="top", fontsize=5.8, color=MUTED)
    for bars in (bars_raw, bars_adapted):
        for bar in bars:
            value = bar.get_height()
            ax_a.text(bar.get_x() + bar.get_width() / 2, value + 0.0008, f"{value:.4f}", ha="center", va="bottom", fontsize=5.9, color=INK)
    ax_a.text(
        0.5,
        -0.20,
        r"gain 95% CI at $10^{-5}$: [0.0024, 0.0250]",
        transform=ax_a.transAxes,
        ha="center",
        va="top",
        fontsize=5.9,
        color=TP,
        clip_on=False,
    )

    raw_ssdd = np.array([float(row["raw_pd"]) for row in ssdd_rows])
    gate_ssdd = np.array([float(row["gate_pd"]) for row in ssdd_rows])
    sx = np.arange(len(ssdd_rows))
    ax_b.plot(sx, raw_ssdd, color=RAW, lw=1.7, marker="o", ms=4.0, label="Raw")
    ax_b.plot(sx, gate_ssdd, color=TP, lw=1.9, marker="^", ms=4.3, label="Gate")
    ax_b.set_xticks(sx)
    ax_b.set_xticklabels([r"$10^{-5}$", r"$3\times10^{-5}$", r"$3\times10^{-4}$"])
    ax_b.set_ylim(0, 0.295)
    ax_b.set_yticks([0, 0.1, 0.2, 0.3])
    ax_b.set_xlabel(r"Target $P_{\mathrm{FA}}$")
    ax_b.set_ylabel(r"$P_{\mathrm{D}}$")
    style_axis(ax_b)
    ax_b.legend(loc="upper left", ncol=2, handlelength=1.2)
    panel_label(ax_b, "b")
    ax_b.set_title("SSDD: supervised adaptation with a raw fallback", loc="left", pad=4, fontweight="bold")
    raw_offsets = [(-10, 7), (-8, 8), (-10, 8)]
    gate_offsets = [(10, 5), (8, -12), (0, 8)]
    for idx, (value, offset) in enumerate(zip(raw_ssdd, raw_offsets)):
        ax_b.annotate(
            f"{value:.4f}",
            (idx, value),
            xytext=offset,
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=5.8,
            color=RAW,
        )
    for idx, (value, offset) in enumerate(zip(gate_ssdd, gate_offsets)):
        ax_b.annotate(
            f"{value:.4f}",
            (idx, value),
            xytext=offset,
            textcoords="offset points",
            ha="center",
            va="bottom" if offset[1] >= 0 else "top",
            fontsize=5.8,
            color=TP,
        )
    ax_b.text(0.02, 0.66, "raw retained in\nthe sparsest tail", transform=ax_b.transAxes, ha="left", va="center", fontsize=6.0, color=RED)
    ax_b.text(0.98, 0.93, "gate becomes useful at $3\\times10^{-4}$", transform=ax_b.transAxes, ha="right", va="top", fontsize=6.0, color=TP)

    fig.subplots_adjust(left=0.18, right=0.98, top=0.97, bottom=0.10)
    save_all(fig, "fig5_external_boundary_singlecol")


def make_fig6() -> None:
    rows = read_csv("fig6_statistical_robustness.csv")
    pfa = np.array([float(row["pfa"]) for row in rows])
    delta_raw = np.array([float(row["delta_raw"]) for row in rows])
    raw_low = np.array([float(row["raw_ci_low"]) for row in rows])
    raw_high = np.array([float(row["raw_ci_high"]) for row in rows])
    delta_res = np.array([float(row["delta_residual"]) for row in rows])
    res_low = np.array([float(row["residual_ci_low"]) for row in rows])
    res_high = np.array([float(row["residual_ci_high"]) for row in rows])
    seed_range = np.array([float(row["seed_pd_range"]) for row in rows])

    fig, (ax_a, ax_b) = plt.subplots(
        2,
        1,
        figsize=(3.50, 4.20),
        gridspec_kw={"height_ratios": [1.45, 1.0], "hspace": 0.43},
    )

    ax_a.errorbar(
        pfa,
        delta_raw,
        yerr=np.vstack((delta_raw - raw_low, raw_high - delta_raw)),
        color=RAW,
        marker="o",
        ms=3.8,
        lw=1.6,
        capsize=2.2,
        elinewidth=0.9,
        label="vs. raw",
    )
    ax_a.errorbar(
        pfa,
        delta_res,
        yerr=np.vstack((delta_res - res_low, res_high - delta_res)),
        color=RES,
        marker="s",
        ms=3.6,
        lw=1.7,
        capsize=2.2,
        elinewidth=0.9,
        label="vs. residual",
    )
    ax_a.axhline(0, color=INK, lw=0.75)
    ax_a.set_xscale("log")
    ax_a.set_xlim(7e-6, 1.4e-2)
    ax_a.set_ylim(-0.005, 0.365)
    ax_a.set_ylabel(r"Paired $\Delta P_{\mathrm{D}}$ (95% CI)")
    ax_a.set_title("Frame-level effect size", loc="left", pad=4, fontweight="bold")
    ax_a.legend(loc="upper left", ncol=2, handlelength=1.4, columnspacing=1.2)
    style_axis(ax_a)
    panel_label(ax_a, "a")
    ax_a.text(
        1.0,
        1.02,
        "210 paired target-bearing frames",
        transform=ax_a.transAxes,
        ha="right",
        va="bottom",
        fontsize=5.9,
        color=MUTED,
        clip_on=False,
    )

    ax_b.plot(pfa, seed_range, color=TP, marker="o", ms=4.0, lw=1.8)
    ax_b.fill_between(pfa, 0, seed_range, color=PALE_GREEN, alpha=0.75)
    ax_b.set_xscale("log")
    ax_b.set_xlim(7e-6, 1.4e-2)
    ax_b.set_ylim(0, 0.0088)
    ax_b.set_yticks([0, 0.004, 0.008])
    ax_b.set_xlabel(r"Target $P_{\mathrm{FA}}$")
    ax_b.set_ylabel(r"Cross-seed $P_{\mathrm{D}}$ range")
    ax_b.set_title("Seed sensitivity", loc="left", pad=4, fontweight="bold")
    style_axis(ax_b)
    panel_label(ax_b, "b")
    max_idx = int(np.argmax(seed_range))
    ax_b.annotate(
        f"max {seed_range[max_idx]:.4f}",
        (pfa[max_idx], seed_range[max_idx]),
        xytext=(-8, 10),
        textcoords="offset points",
        ha="right",
        va="bottom",
        fontsize=6.0,
        color=TP,
        arrowprops={"arrowstyle": "-", "color": TP, "lw": 0.7},
    )
    ax_b.text(
        0.02,
        0.92,
        "seeds 7, 11, 23; 21/21 wins vs. both comparators",
        transform=ax_b.transAxes,
        ha="left",
        va="top",
        fontsize=5.8,
        color=MUTED,
    )

    fig.subplots_adjust(left=0.19, right=0.98, top=0.96, bottom=0.12)
    save_all(fig, "fig6_statistical_robustness_singlecol")


def make_fig7() -> None:
    data = np.load(DATA / "fig7_aistap_case_audit.npz")
    cases = ["success", "failure"]
    row_titles = [
        r"Selected rescue: $P_D$ raw/res./TP = 0.067/0.133/0.400",
        r"Selected failure: $P_D$ raw/res./TP = 0.120/0.000/0.000",
    ]
    column_titles = ["Raw score", "Rank-30 residual", "Gate raw weight"]

    fig, axes = plt.subplots(2, 3, figsize=(3.50, 3.10))
    for row, (case, row_title) in enumerate(zip(cases, row_titles)):
        mask = data[f"{case}_mask"].astype(bool)
        coordinates = np.argwhere(mask)
        arrays = [data[f"{case}_raw"], data[f"{case}_residual"], data[f"{case}_gate"]]
        for column, (ax, array) in enumerate(zip(axes[row], arrays)):
            ax.imshow(array, aspect="auto", cmap="magma", vmin=0.0, vmax=1.0, interpolation="nearest")
            scatter_options = {
                "s": 7.5,
                "edgecolors": "#38D7FF",
                "linewidths": 0.48,
            }
            if column == 2:
                scatter_options.update(
                    {
                        "c": array[coordinates[:, 0], coordinates[:, 1]],
                        "cmap": "magma",
                        "vmin": 0.0,
                        "vmax": 1.0,
                    }
                )
            else:
                scatter_options["facecolors"] = "none"
            ax.scatter(coordinates[:, 1], coordinates[:, 0], **scatter_options)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color("#D7DCE4")
                spine.set_linewidth(0.55)
            if row == 0:
                ax.set_title(column_titles[column], pad=2.0, fontsize=6.7, fontweight="bold")
        axes[row, 0].text(
            0.0,
            1.07,
            row_title,
            transform=axes[row, 0].transAxes,
            ha="left",
            va="bottom",
            fontsize=6.1,
            color=INK,
            clip_on=False,
        )
        panel_label(axes[row, 0], chr(ord("a") + row), x=-0.22, y=1.05)

    fig.text(
        0.5,
        0.015,
        "Cyan markers: target cells; gate-column fill encodes weight. Scores use 1%-99.9% normalized log scale.",
        ha="center",
        va="bottom",
        fontsize=5.5,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.055, right=0.995, top=0.91, bottom=0.09, wspace=0.06, hspace=0.38)
    save_all(fig, "fig7_aistap_case_audit_singlecol")


def main() -> None:
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    make_fig5()
    make_fig6()
    make_fig7()


if __name__ == "__main__":
    main()
