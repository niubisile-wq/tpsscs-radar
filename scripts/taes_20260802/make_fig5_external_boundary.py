from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np


OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 8,
        "axes.linewidth": 0.8,
        "figure.dpi": 180,
        "axes.labelcolor": "#1F2A37",
        "xtick.color": "#1F2A37",
        "ytick.color": "#1F2A37",
        "text.color": "#1F2A37",
    }
)


INK = "#1F2A37"
MUTED = "#667085"
GRID = "#E8EBF0"
RAW = "#9AA5B1"
FUSION = "#4C78A8"
GATE = "#5BA05B"
RED = "#D94B4B"
BLUE_BG = "#EAF2FF"
GREEN_BG = "#EAF7EA"
RED_BG = "#FBECEC"
GREY_BG = "#F3F5F7"


def panel_label(ax, label, x=0.01, y=0.98):
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        fontweight="bold",
        color=INK,
    )


def rounded_box(ax, xy, wh, fc, ec, txt, txt_color=INK, fontsize=9.0, weight="bold"):
    box = patches.FancyBboxPatch(
        xy,
        wh[0],
        wh[1],
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.0,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + wh[0] / 2,
        xy[1] + wh[1] / 2,
        txt,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        color=txt_color,
    )
    return box


fig = plt.figure(figsize=(7.35, 4.95), constrained_layout=False)
gs = fig.add_gridspec(
    2,
    2,
    height_ratios=[1.15, 1.0],
    width_ratios=[1.0, 1.0],
    hspace=0.38,
    wspace=0.28,
)

ax_top = fig.add_subplot(gs[0, :])
ax_ipix = fig.add_subplot(gs[1, 0])
ax_ssdd = fig.add_subplot(gs[1, 1])

for ax in (ax_top, ax_ipix, ax_ssdd):
    ax.set_facecolor("white")

fig.text(
    0.5,
    0.975,
    "External boundary checks separate domain-shift failure from bounded adaptation",
    ha="center",
    va="top",
    fontsize=9.2,
    fontweight="bold",
    color=INK,
)

# Panel a: overview schematic
ax_top.set_xlim(0, 1)
ax_top.set_ylim(0, 1)
ax_top.axis("off")
panel_label(ax_top, "a")

ax_top.add_patch(
    patches.FancyBboxPatch(
        (0.02, 0.12),
        0.96,
        0.74,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=0.9,
        edgecolor="#D8DEE9",
        facecolor="#FBFCFE",
    )
)

ax_top.text(
    0.5,
    0.80,
    "AISTAP-SIM is the fixed in-domain anchor; IPIX and SSDD are boundary checks",
    ha="center",
    va="center",
    fontsize=8.5,
    color=INK,
    fontweight="bold",
)

rounded_box(ax_top, (0.05, 0.38), (0.22, 0.18), BLUE_BG, FUSION, "AISTAP-SIM\nofficial full assets", fontsize=8.3)
rounded_box(ax_top, (0.36, 0.38), (0.20, 0.18), RED_BG, RED, "IPIX\nzero-shot transfer", fontsize=8.3)
rounded_box(ax_top, (0.68, 0.38), (0.22, 0.18), GREEN_BG, GATE, "SSDD\nsupervised adaptation", fontsize=8.3)

ax_top.annotate(
    "",
    xy=(0.36, 0.47),
    xytext=(0.27, 0.47),
    arrowprops=dict(arrowstyle="->", lw=1.3, color=RED),
)
ax_top.text(0.315, 0.54, "direct zero-shot is negative", ha="center", va="bottom", fontsize=7.2, color=RED)

ax_top.annotate(
    "",
    xy=(0.68, 0.47),
    xytext=(0.58, 0.47),
    arrowprops=dict(arrowstyle="->", lw=1.3, color=GATE),
)
ax_top.text(0.63, 0.54, "supervised adaptation", ha="center", va="bottom", fontsize=7.2, color=GATE)

ax_top.add_patch(patches.Circle((0.36, 0.47), 0.034, facecolor="white", edgecolor=RED, linewidth=1.1))
ax_top.text(0.36, 0.47, "X", ha="center", va="center", fontsize=12, fontweight="bold", color=RED)
ax_top.add_patch(patches.Circle((0.68, 0.47), 0.034, facecolor="white", edgecolor=GATE, linewidth=1.1))
ax_top.text(0.68, 0.47, "OK", ha="center", va="center", fontsize=8.8, fontweight="bold", color=GATE)

ax_top.text(
    0.10,
    0.24,
    "in-domain anchor",
    ha="left",
    va="center",
    fontsize=7.2,
    color=FUSION,
    fontweight="bold",
)
ax_top.text(
    0.44,
    0.24,
    "zero-shot boundary",
    ha="center",
    va="center",
    fontsize=7.2,
    color=RED,
    fontweight="bold",
)
ax_top.text(
    0.81,
    0.24,
    "supervised boundary",
    ha="center",
    va="center",
    fontsize=7.2,
    color=GATE,
    fontweight="bold",
)

# Panel b: IPIX selected fusion
panel_label(ax_ipix, "b")

pfa = np.array([1, 2])
x = np.arange(len(pfa))
bar_w = 0.34
raw = np.array([0.0513, 0.0532])
fusion = np.array([0.0644, 0.0695])

ax_ipix.bar(x - bar_w / 2, raw, width=bar_w, color=RAW, edgecolor="white", linewidth=0.8, label="Raw")
ax_ipix.bar(
    x + bar_w / 2,
    fusion,
    width=bar_w,
    color=FUSION,
    edgecolor="white",
    linewidth=0.8,
    label="Validation-selected fusion",
)
for xi, r, f in zip(x, raw, fusion):
    ax_ipix.text(xi - bar_w / 2, r + 0.0012, f"{r:.4f}", ha="center", va="bottom", fontsize=7.0, color=RAW)
    ax_ipix.text(xi + bar_w / 2, f + 0.0012, f"{f:.4f}", ha="center", va="bottom", fontsize=7.0, color=FUSION)
    ax_ipix.text(xi, max(r, f) + 0.0046, f"+{(f-r):.4f}", ha="center", va="bottom", fontsize=7.0, color=GATE)

ax_ipix.set_xticks(x)
ax_ipix.set_xticklabels([r"$10^{-5}$", r"$10^{-4}$"], fontsize=8)
ax_ipix.set_ylabel(r"$P_{\mathrm{D}}$", labelpad=3)
ax_ipix.set_title("IPIX held-out recordings", fontsize=8.4, fontweight="bold", pad=4)
ax_ipix.set_ylim(0.045, 0.0785)
ax_ipix.set_yticks([0.05, 0.06, 0.07, 0.08])
ax_ipix.grid(True, axis="y", color=GRID, linewidth=0.7)
ax_ipix.set_axisbelow(True)
ax_ipix.spines["top"].set_visible(False)
ax_ipix.spines["right"].set_visible(False)
ax_ipix.tick_params(length=3, width=0.8)
ax_ipix.text(
    0.5,
    1.02,
    "one held-out recording for selection, 12 disjoint test recordings",
    transform=ax_ipix.transAxes,
    ha="center",
    va="bottom",
    fontsize=6.7,
    color=MUTED,
)
ax_ipix.text(
    0.5,
    -0.22,
    "Gain CI at $10^{-5}$: [0.0024, 0.0250]",
    transform=ax_ipix.transAxes,
    ha="center",
    va="top",
    fontsize=6.8,
    color=INK,
)

# Panel c: SSDD boundary trend
panel_label(ax_ssdd, "c")

xs = np.array([1e-5, 3e-5, 3e-4])
raw_ssdd = np.array([0.0188, 0.0373, 0.1625])
gate_ssdd = np.array([0.0035, 0.0291, 0.2630])

ax_ssdd.plot(xs, raw_ssdd, color=RAW, lw=1.9, marker="o", ms=5.5, label="Raw")
ax_ssdd.plot(xs, gate_ssdd, color=GATE, lw=2.2, marker="^", ms=5.8, label="Gate")
ax_ssdd.set_xscale("log")
ax_ssdd.set_xlim(7e-6, 5e-4)
ax_ssdd.set_ylim(0.0, 0.30)
ax_ssdd.set_xticks(xs)
ax_ssdd.set_xticklabels([r"$10^{-5}$", r"$3\times10^{-5}$", r"$3\times10^{-4}$"], fontsize=7.8)
ax_ssdd.set_yticks([0.0, 0.1, 0.2, 0.3])
ax_ssdd.set_xlabel(r"Target $P_{\mathrm{FA}}$", labelpad=3)
ax_ssdd.set_ylabel(r"$P_{\mathrm{D}}$", labelpad=3)
ax_ssdd.set_title("SSDD adaptation boundary", fontsize=8.4, fontweight="bold", pad=4)
ax_ssdd.grid(True, which="major", color=GRID, linewidth=0.7)
ax_ssdd.set_axisbelow(True)
ax_ssdd.spines["top"].set_visible(False)
ax_ssdd.spines["right"].set_visible(False)
ax_ssdd.tick_params(length=3, width=0.8)

for x0, y0 in zip(xs, raw_ssdd):
    ax_ssdd.text(x0, y0 + 0.009, f"{y0:.4f}", ha="center", va="bottom", fontsize=6.7, color=RAW)
for x0, y0 in zip(xs, gate_ssdd):
    ax_ssdd.text(x0, y0 + 0.009, f"{y0:.4f}", ha="center", va="bottom", fontsize=6.7, color=GATE)

ax_ssdd.annotate(
    "raw fallback\nat strictest tail",
    xy=(1e-5, raw_ssdd[0]),
    xytext=(1.35e-5, 0.070),
    textcoords="data",
    fontsize=6.8,
    color=RED,
    ha="left",
    va="bottom",
    arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.0, shrinkA=0, shrinkB=0),
)
ax_ssdd.annotate(
    "gate wins once the tail is less sparse",
    xy=(3e-4, gate_ssdd[-1]),
    xytext=(1.7e-4, 0.282),
    textcoords="data",
    fontsize=6.8,
    color=GATE,
    ha="center",
    va="bottom",
    arrowprops=dict(arrowstyle="-|>", color=GATE, lw=1.0, shrinkA=0, shrinkB=0),
)

ax_ssdd.legend(loc="upper left", fontsize=6.9, frameon=False, handlelength=2.0)

fig.subplots_adjust(left=0.065, right=0.985, top=0.90, bottom=0.13)
fig.patch.set_facecolor("white")

fig.savefig(OUT / "fig5_external_boundary.pdf", bbox_inches="tight")
fig.savefig(OUT / "fig5_external_boundary.svg", bbox_inches="tight")
fig.savefig(OUT / "fig5_external_boundary.png", dpi=240, bbox_inches="tight")
fig.savefig(OUT / "fig5_external_boundary.tiff", dpi=600, bbox_inches="tight")
