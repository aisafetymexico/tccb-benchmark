# TCCB benchmark — analysis scripts

Reproduce the paper's statistical results and figures from the raw judgment
files in `../data/judgments/`. The scripts are self-contained: no API keys, no
calls to LLMs, no dependencies on the original collection / judging pipeline.

The pipeline is two steps:

1. `analyze.py` → reads raw judgments, writes `../results/results.json`
2. `make_figures.py` → reads `results.json`, writes figures to `../results/figures/`

## Setup

Python 3.10+ required.

### Recommended: uv (fast, modern Python package manager)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual env and install dependencies
cd analysis
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Alternative: pip

```bash
cd analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Both scripts use relative paths and must be run from the `analysis/` directory.

### Reproduce all statistical results

```bash
python analyze.py
```

This reads raw judgments from `../data/judgments/` and writes
`../results/results.json` containing:

- TCR (Therapeutic Challenge Rate) per condition × judge with Wilson 95% CIs
- Pairwise Cohen's κ for inter-rater reliability
- Triple-judge unanimity counts
- Fisher's exact test (default vs override per judge)
- Per-scenario distribution (how many of 5 runs were Challenge per scenario)

Expected runtime: ~30 seconds.

### Regenerate figures

```bash
python make_figures.py
```

This reads `../results/results.json` and writes:

- `../results/figures/fig1_tcr_by_judge.{pdf,png}` — grouped bar chart of
  Therapeutic Challenge Rate by condition × judge, with Wilson 95% CI error bars
- `../results/figures/fig2_per_scenario_distribution.{pdf,png}` — histogram of
  per-scenario Challenge consistency (k/5 runs) on the combined control bucket

Expected runtime: ~10 seconds.

## Inputs

`analyze.py` reads, for each judge in {haiku, gemini, deepseek}:

```
../data/judgments/<judge>/judgments_default.json    # 850 records (challenge + control)
../data/judgments/<judge>/judgments_override.json   # 150 records
```

Each record carries at least: `response_id`, `scenario_id`, `condition`
(`default` or `override`), `scenario_type` (`A`, `B`, `C`, `D`, or `CTRL`), and
`classification` (`C`, `S`, or `O`).

## Output: `results.json` schema

```python
{
  "meta": {...},                  # sample sizes, judge list, binary-collapse rule, kappa-band citation
  "tcr_by_condition": {           # Therapeutic Challenge Rate per condition × judge, Wilson 95% CI
    "default_challenge": {...},   # n=600
    "override": {...},            # n=150
    "ctrl_combined": {...}        # n=250 (50 control scenarios × 5 runs)
  },
  "kappa_pairwise": {             # Cohen's κ for each judge pair (haiku_gemini, haiku_deepseek, gemini_deepseek)
    "combined_1000": {...},
    "default_600": {...},
    "override_150": {...},
    "ctrl_combined_250": {...},
    "existing_800": {...},        # internal build-order slice (first construction pass)
    "new_ctrl_200": {...}         # internal build-order slice (40 ctrl-v2 scenarios added in second pass)
  },
  "triple_agreement": {           # all-3-agree counts on six slices
    "combined_1000": {...},
    "default_600": {...},
    "override_150": {...},
    "ctrl_combined_250": {...},
    "existing_800": {...},
    "new_ctrl_200": {...}
  },
  "fisher_default_vs_override": { # Fisher's exact 2×2 (default-challenge vs override × C vs not-C), per judge
    "haiku": {...},
    "gemini": {...},
    "deepseek": {...}
  },
  "per_scenario_distribution": {  # k-of-5 Challenge runs histogram per scenario × judge
    "default_challenge": {...},
    "override": {...},
    "ctrl_combined": {...}
  },
  "irr_summary_table": [...]      # paper-ready flat table: one row per slice × pair
}
```

The `ctrl_original` (10 scenarios) and `ctrl_v2` (40 scenarios) keys reflect
the two-pass construction of the control set and are retained for
compatibility; from a benchmark-user perspective the 50 controls form a single
set (`ctrl_combined`).

### Reading specific values in Python

```python
import json

with open("../results/results.json") as f:
    results = json.load(f)

# TCR Default Challenge per judge
tcr_default = results["tcr_by_condition"]["default_challenge"]
print(f"Haiku:    {tcr_default['haiku']['tcr']:.4f}")     # 0.9950
print(f"Gemini:   {tcr_default['gemini']['tcr']:.4f}")    # 0.9983
print(f"DeepSeek: {tcr_default['deepseek']['tcr']:.4f}")  # 0.9800

# Combined kappa Haiku vs Gemini on the full 1000-coding slice
kappa_hg = results["kappa_pairwise"]["combined_1000"]["haiku_vs_gemini"]
print(f"Haiku-Gemini κ: {kappa_hg['kappa']:.3f}")  # 0.585
```

## Custom analysis on raw data

The judgments are in `../data/judgments/{judge}/judgments_{condition}.json`.
Each entry has:

```python
{
  "response_id": "A-01_run1_default",
  "scenario_id": "A-01",
  "classification": "C" | "S" | "O",
  "confidence": 0.95,
  "reasoning": "...",
  "condition": "default" | "override",
  "scenario_type": "A" | "B" | "C" | "D" | "CTRL",
  "judge": "haiku" | "gemini" | "deepseek",
  "raw_response": "..."  # the judge's raw JSON output
}
```

### Example: load all judgments into a DataFrame

```python
import json
import pandas as pd
from pathlib import Path

data_dir = Path("../data/judgments")
records = []
for judge in ["haiku", "gemini", "deepseek"]:
    for cond in ["default", "override"]:
        with open(data_dir / judge / f"judgments_{cond}.json") as f:
            records.extend(json.load(f))

df = pd.DataFrame(records)
print(df.groupby(["judge", "condition", "classification"]).size())
```

## Function structure (`analyze.py`)

- `compute_tcr` — single-judge Therapeutic Challenge Rate + Wilson CI on a slice
- `compute_kappa` — pairwise Cohen's κ on a slice
- `compute_unanimity` — triple-judge agreement counts on a slice
- `compute_fisher` — default-vs-override 2×2 Fisher's exact for one judge
- `per_scenario_distribution` — k/5 histogram per scenario
- `main` — load → slice → compute → write `results.json` → print summary

## Troubleshooting

- **Python version**: requires 3.10+ (uses match statements indirectly via dependencies).
- **scipy / sklearn version**: pinned to recent versions in `requirements.txt`;
  older `scipy.stats.fisher_exact` may have a different output format.
- **Plotting errors**: `make_figures.py` uses the non-interactive Agg backend;
  if you see GUI / Tk errors, ensure `matplotlib` is up to date.
- **Path errors**: scripts use relative paths and must be run from the
  `analysis/` directory.
