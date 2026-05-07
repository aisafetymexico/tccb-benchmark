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

    ax.set_ylabel("Therapeutic Competence Rate (TCR)")
    ax.set_xticks(x)
    ax.set_xticklabels([label for _, label in conditions])
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.legend(loc="lower left", frameon=True, framealpha=0.95, fontsize=10)
    ax.axhline(y=1.0, linestyle=":", color="gray", linewidth=0.5)

    fig.tight_layout()
    _save(fig, output_path)


def fig2_per_scenario_distribution(results: dict, output_path: Path) -> None:
    """Per-scenario challenge consistency on the combined control bucket (k/5 runs)."""
    dist_haiku = results["per_scenario_distribution"]["ctrl_combined"]["haiku"]
    histogram = dist_haiku["k_to_count"]

    x_values = list(range(6))
    counts = [histogram.get(str(k), 0) for k in x_values]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(x_values, counts, color=JUDGE_COLORS["haiku"],
                  edgecolor="black", linewidth=0.8, width=0.6)

    ax.set_xlabel("Challenge Runs (out of 5)")
    ax.set_ylabel("Number of Scenarios")
    ax.set_title("Per-Scenario Challenge Consistency (Control bucket, Haiku judge)")
    ax.set_xticks(x_values)
    ax.set_xticklabels([str(v) for v in x_values])

    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                    str(count), ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylim(0, max(counts) * 1.15 if counts and max(counts) else 1)
    fig.tight_layout()
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
