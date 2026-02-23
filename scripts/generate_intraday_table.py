"""
generate_intraday_table.py
--------------------------
Reads the intraday model comparison results and outputs a clean
summary table as a PNG image saved to results/.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import os

# ── Paths ────────────────────────────────────────────────────────────────────
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
OUTPUT_PATH = os.path.join(RESULTS_DIR, "intraday_results_table.png")

# ── Data (from model_comparison_intraday.md) ─────────────────────────────────

# Holdout test results
holdout_headers = ["Model", "Accuracy", "Precision\n(Up)", "Recall\n(Up)", "F1-Score\n(Up)"]
holdout_rows = [
    ["Technical Only",         "48.84%", "68.42%", "44.83%", "54.17%"],
    ["Sentiment Only",         "62.79%", "78.26%", "62.07%", "69.23%"],
    ["Technical + Sentiment",  "55.81%", "70.83%", "58.62%", "64.15%"],
    ["Majority Class Baseline","67.44%", "—",       "—",      "—"     ],
    ["Coin Toss Baseline",     "50.00%", "—",       "—",      "—"     ],
]

# Cross-validation results
cv_headers = ["Model", "Accuracy", "Precision\n(Up)", "Recall\n(Up)", "F1-Score\n(Up)"]
cv_rows = [
    ["Technical Only",        "45.22% ± 12.48%", "44.30% ± 29.43%", "37.50% ± 19.88%", "38.91% ± 23.40%"],
    ["Sentiment Only",        "47.83% ± 13.75%", "55.87% ± 21.06%", "50.26% ± 11.96%", "50.80% ± 15.18%"],
    ["Technical + Sentiment", "50.43% ± 10.86%", "64.15% ± 19.28%", "47.18% ± 18.48%", "48.63% ± 14.78%"],
]

# McNemar's test results
mcnemar_headers = ["Comparison", "Discordant\nPairs (b, c)", "p-value", "Significant?"]
mcnemar_rows = [
    ["Technical Only vs. Combined",      "(5, 8)", "0.5811", "No  (p ≥ 0.05)"],
    ["Sentiment Only vs. Combined",      "(5, 2)", "0.4531", "No  (p ≥ 0.05)"],
    ["Technical Only vs. Sentiment Only","(7, 13)","0.2632", "No  (p ≥ 0.05)"],
]

# ── Colour palette ────────────────────────────────────────────────────────────
HEADER_BG     = "#1a1a2e"   # dark navy
HEADER_FG     = "#ffffff"
TECH_BG       = "#e8f4f8"   # light blue tint  — Technical Only
SENT_BG       = "#e8f8e8"   # light green tint — Sentiment Only
COMB_BG       = "#f8f4e8"   # light amber tint — Combined
BASE_BG       = "#f0f0f0"   # light grey       — baselines
ROW_BG_ALT    = "#fafafa"
BORDER        = "#cccccc"
TITLE_COLOR   = "#1a1a2e"
SUBTITLE_COLOR= "#555555"

MODEL_COLORS = {
    "Technical Only":         TECH_BG,
    "Sentiment Only":         SENT_BG,
    "Technical + Sentiment":  COMB_BG,
    "Majority Class Baseline":BASE_BG,
    "Coin Toss Baseline":     BASE_BG,
}

def draw_table(ax, headers, rows, row_colors=None, col_widths=None):
    """Draw a styled table on the given axes."""
    ax.axis("off")

    n_cols = len(headers)
    n_rows = len(rows) + 1  # +1 for header

    if col_widths is None:
        col_widths = [1.0 / n_cols] * n_cols

    row_height = 1.0 / n_rows
    xs = []
    x = 0
    for w in col_widths:
        xs.append(x)
        x += w

    def draw_cell(x, y, w, h, text, bg, fg="#222222", bold=False, fontsize=9):
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="square,pad=0",
            linewidth=0.6,
            edgecolor=BORDER,
            facecolor=bg,
            transform=ax.transAxes,
            clip_on=False,
        )
        ax.add_patch(rect)
        ax.text(
            x + w / 2, y + h / 2, text,
            ha="center", va="center",
            fontsize=fontsize,
            color=fg,
            fontweight="bold" if bold else "normal",
            transform=ax.transAxes,
            wrap=True,
            multialignment="center",
        )

    # Header row
    y = 1.0 - row_height
    for i, (header, w, xpos) in enumerate(zip(headers, col_widths, xs)):
        draw_cell(xpos, y, w, row_height, header, HEADER_BG, fg=HEADER_FG, bold=True, fontsize=9)

    # Data rows
    for r_idx, row in enumerate(rows):
        y = 1.0 - row_height * (r_idx + 2)
        for c_idx, (cell, w, xpos) in enumerate(zip(row, col_widths, xs)):
            model_name = row[0]
            if row_colors and model_name in row_colors:
                bg = row_colors[model_name]
            else:
                bg = ROW_BG_ALT if r_idx % 2 == 0 else "#ffffff"
            draw_cell(xpos, y, w, row_height, cell, bg, fontsize=8.5)


# ── Layout ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(10, 5), facecolor="white")
fig.patch.set_facecolor("white")

gs = GridSpec(
    1, 1,
    figure=fig,
    top=0.82,
    bottom=0.18,
    left=0.03,
    right=0.97,
)

# ── Main title ────────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.97,
    "Experiment 2 — Intraday Prediction: Holdout Test Results",
    ha="center", va="top",
    fontsize=13, fontweight="bold", color=TITLE_COLOR,
)
fig.text(
    0.5, 0.90,
    "Apple Inc. (AAPL) · Test Period: 2024-08-30 to 2024-12-23 · 43 observations  |  "
    "Model: Logistic Regression (L2, balanced)",
    ha="center", va="top",
    fontsize=8.5, color=SUBTITLE_COLOR,
)

# ── Holdout test results table ────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0])
draw_table(
    ax1,
    holdout_headers,
    holdout_rows,
    row_colors=MODEL_COLORS,
    col_widths=[0.34, 0.165, 0.165, 0.165, 0.165],
)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(facecolor=TECH_BG, edgecolor=BORDER, label="Technical Only"),
    mpatches.Patch(facecolor=SENT_BG, edgecolor=BORDER, label="Sentiment Only"),
    mpatches.Patch(facecolor=COMB_BG, edgecolor=BORDER, label="Technical + Sentiment"),
    mpatches.Patch(facecolor=BASE_BG, edgecolor=BORDER, label="Baselines"),
]
fig.legend(
    handles=legend_items,
    loc="lower center",
    ncol=4,
    fontsize=8.5,
    frameon=True,
    framealpha=0.9,
    edgecolor=BORDER,
    bbox_to_anchor=(0.5, 0.01),
)

# ── Save ──────────────────────────────────────────────────────────────────────
os.makedirs(RESULTS_DIR, exist_ok=True)
plt.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved: {OUTPUT_PATH}")
