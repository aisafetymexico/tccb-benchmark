"""Standalone figure generation for the TCCB benchmark.

Reads ../results/results.json (produced by analyze.py) and writes:
  - ../results/figures/fig1_tcr_by_judge.{pdf,png}
  - ../results/figures/fig2_per_scenario_distribution.{pdf,png}

Self-contained: depends only on stdlib + numpy + matplotlib + seaborn.
Run from this directory: `python make_figures.py`.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT.parent / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

JUDGES = ["haiku", "gemini", "deepseek"]
JUDGE_COLORS = {"haiku": "#4878A8", "gemini": "#E8853A", "deepseek": "#7BAA6E"}
JUDGE_LABELS = {"haiku": "Claude Haiku", "gemini": "Gemini 2.5 Flash", "deepseek": "DeepSeek-Chat"}

# Colorblind-safe palette (Wong/Tol) used by the paper's fig2.
FIG2_JUDGE_COLORS = {"haiku": "#0173B2", "gemini": "#DE8F05", "deepseek": "#029E73"}

FIG2_PANELS = [
    ("default_challenge", "Challenge-prescribed scenarios (n = 120)"),
    ("ctrl_combined",     "Validation-appropriate scenarios (n = 50)"),
]


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def fig1_tcr_by_judge(results: dict, output_path: Path) -> None:
    """Grouped bar chart: TCR by condition × judge with Wilson 95% CI error bars."""
    tcr = results["tcr_by_condition"]
    conditions = [
        ("default_challenge", "Default\nChallenge"),
        ("override",          "Override"),
        ("ctrl_combined",     "Control\n(combined)"),
    ]

    bar_width = 0.25
    x = np.arange(len(conditions))

    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for i, judge in enumerate(JUDGES):
        tcrs  = [tcr[c][judge]["tcr"]           for c, _ in conditions]
        ci_lo = [tcr[c][judge]["wilson_ci_lo"]  for c, _ in conditions]
        ci_hi = [tcr[c][judge]["wilson_ci_hi"]  for c, _ in conditions]
        err_lo = [t - lo for t, lo in zip(tcrs, ci_lo)]
        err_hi = [hi - t for t, hi in zip(tcrs, ci_hi)]

        positions = x + (i - 1) * bar_width
        bars = ax.bar(
            positions, tcrs, bar_width,
            yerr=[err_lo, err_hi], capsize=4,
            color=JUDGE_COLORS[judge], edgecolor="black", linewidth=0.6,
            label=JUDGE_LABELS[judge],
        )
        for bar, t in zip(bars, tcrs):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.015,
                    f"{t * 100:.1f}", ha="center", va="bottom", fontsize=9)

    ax.set_ylabel("Therapeutic Challenge Rate (TCR)")
    ax.set_xticks(x)
    ax.set_xticklabels([label for _, label in conditions])
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.legend(loc="lower left", frameon=True, framealpha=0.95, fontsize=10)
    ax.axhline(y=1.0, linestyle=":", color="gray", linewidth=0.5)

    fig.tight_layout()
    _save(fig, output_path)


def fig2_per_scenario_distribution(results: dict, output_path: Path) -> None:
    """Two-panel cross-judge per-scenario distribution.

    Left  — Challenge-prescribed scenarios (n=120 per judge)
    Right — Validation-appropriate scenarios (n=50 per judge)
    Each panel: grouped bars (Haiku/Gemini/DeepSeek) over k = 0..5 Challenge runs.
    """
    distrib = results["per_scenario_distribution"]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), sharey=False)

    bar_width = 0.27
    x_positions = np.arange(6)

    for ax, (cond_key, panel_title) in zip(axes, FIG2_PANELS):
        max_count = 0
        for i, judge in enumerate(JUDGES):
            k_to_count = distrib[cond_key][judge]["k_to_count"]
            counts = [int(k_to_count.get(str(k), 0)) for k in range(6)]
            max_count = max(max_count, max(counts))
            offsets = (i - 1) * bar_width
            bars = ax.bar(
                x_positions + offsets,
                counts,
                bar_width,
                color=FIG2_JUDGE_COLORS[judge],
                edgecolor="black",
                linewidth=0.5,
                label=JUDGE_LABELS[judge],
            )
            for bar, c in zip(bars, counts):
                if c > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(0.5, max_count * 0.012),
                        str(c),
                        ha="center",
                        va="bottom",
                        fontsize=8,
                    )

        ax.set_xticks(x_positions)
        ax.set_xticklabels([str(v) for v in range(6)])
        ax.set_xlabel("Number of Challenge runs (out of 5)")
        ax.set_title(panel_title, fontsize=11)
        ax.set_ylim(0, max_count * 1.18)
        ax.grid(axis="x", visible=False)

    axes[0].set_ylabel("Number of scenarios")
    axes[1].set_ylabel("Number of scenarios")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles, labels,
        loc="lower center", ncol=3, frameon=True, framealpha=0.95,
        bbox_to_anchor=(0.5, -0.02), fontsize=10,
    )

    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _save(fig, output_path)


def main() -> None:
    sns.set_style("whitegrid")
    plt.rcParams.update({"font.size": 12})

    results_path = RESULTS_DIR / "results.json"
    with open(results_path) as fp:
        results = json.load(fp)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig1_tcr_by_judge(results, FIGURES_DIR / "fig1_tcr_by_judge")
    fig2_per_scenario_distribution(results, FIGURES_DIR / "fig2_per_scenario_distribution")
    print(f"Wrote figures to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
