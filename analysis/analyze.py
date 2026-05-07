"""Standalone TCCB benchmark analysis.

Reads per-judge judgment files from ../data/judgments/{judge}/judgments_{condition}.json,
recomputes all paper statistics from raw, writes ../results/results.json, and
prints a human-readable summary to stdout.

Self-contained: depends only on stdlib + numpy + pandas + scipy + sklearn.
Run from this directory: `python analyze.py`.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, norm
from sklearn.metrics import cohen_kappa_score


ROOT = Path(__file__).resolve().parent
JUDGMENTS_DIR = ROOT.parent / "data" / "judgments"
RESULTS_DIR = ROOT.parent / "results"

JUDGES = ["haiku", "gemini", "deepseek"]
CONDITIONS = ["default", "override"]


# ---------------------------------------------------------------------------
# Loading & normalization
# ---------------------------------------------------------------------------

def _parse_run(response_id: str) -> str:
    for part in response_id.split("_"):
        if part.startswith("run"):
            return part
    raise ValueError(f"no run segment in response_id: {response_id!r}")


def _composite_key(scenario_id: str, run: str, condition: str) -> str:
    return f"{scenario_id}_{run}_{condition}"


def load_judge(judge: str) -> pd.DataFrame:
    rows: list[dict] = []
    for cond in CONDITIONS:
        path = JUDGMENTS_DIR / judge / f"judgments_{cond}.json"
        with open(path) as fp:
            data = json.load(fp)
        for rec in data:
            run = _parse_run(rec["response_id"])
            rows.append({
                "key": _composite_key(rec["scenario_id"], run, rec["condition"]),
                "scenario_id": rec["scenario_id"],
                "run": run,
                "condition": rec["condition"],
                "scenario_type": rec["scenario_type"],
                f"{judge}_class": rec["classification"],
            })
    df = pd.DataFrame(rows).drop_duplicates(subset=["key"]).reset_index(drop=True)
    return df


def build_unified_frame() -> pd.DataFrame:
    haiku = load_judge("haiku")
    gemini = load_judge("gemini")
    deepseek = load_judge("deepseek")

    base = ["key", "scenario_id", "run", "condition", "scenario_type"]
    df = (
        haiku[base + ["haiku_class"]]
        .merge(gemini[["key", "gemini_class"]], on="key", how="outer")
        .merge(deepseek[["key", "deepseek_class"]], on="key", how="outer")
    )

    def bucket(row: pd.Series) -> str:
        if row["scenario_type"] != "CTRL":
            return "default_challenge" if row["condition"] == "default" else "override"
        try:
            n = int(row["scenario_id"].split("-")[1])
        except (IndexError, ValueError):
            return "ctrl_unknown"
        return "ctrl_original" if n <= 10 else "ctrl_v2"

    df["bucket"] = df.apply(bucket, axis=1)
    return df


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def is_challenge(label) -> bool:
    """Binary collapse: literal 'C' is Challenge; everything else (S, O, NaN) is not."""
    return isinstance(label, str) and label == "C"


def wilson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval (no continuity correction).

    Computation order mirrors statsmodels.stats.proportion.proportion_confint(method='wilson')
    to be ULP-identical.
    """
    if n == 0:
        return (float("nan"), float("nan"))
    q = k / n
    crit = norm.isf(alpha / 2.0)
    crit2 = crit ** 2
    denom = 1 + crit2 / n
    center = (q + crit2 / (2 * n)) / denom
    dist = crit * np.sqrt(q * (1.0 - q) / n + crit2 / (4.0 * n ** 2)) / denom
    return (float(center - dist), float(center + dist))


def interpret_kappa(k: float) -> str:
    """Landis & Koch (1977) bands."""
    if k != k:  # NaN
        return "almost-perfect"
    if k < 0:
        return "poor (worse than chance)"
    if k < 0.20:
        return "slight"
    if k < 0.40:
        return "fair"
    if k < 0.60:
        return "moderate"
    if k < 0.80:
        return "substantial"
    return "almost-perfect"


# ---------------------------------------------------------------------------
# Core computations
# ---------------------------------------------------------------------------

def compute_tcr(df: pd.DataFrame, judge: str) -> dict:
    col = f"{judge}_class"
    n = int(df[col].notna().sum())
    k = int(df[col].apply(is_challenge).sum())
    tcr = k / n if n else float("nan")
    lo, hi = wilson_ci(k, n)
    return {
        "n": n,
        "k_challenge": k,
        "tcr": tcr,
        "wilson_ci_lo": float(lo),
        "wilson_ci_hi": float(hi),
    }


def compute_kappa(df: pd.DataFrame, j1: str, j2: str) -> dict:
    c1, c2 = f"{j1}_class", f"{j2}_class"
    sub = df.dropna(subset=[c1, c2])
    if len(sub) == 0:
        return {"n": 0, "agreement": float("nan"), "kappa": float("nan"), "interpretation": "n/a"}
    y1 = sub[c1].apply(is_challenge).astype(int).to_numpy()
    y2 = sub[c2].apply(is_challenge).astype(int).to_numpy()
    agreement = float((y1 == y2).mean())
    kappa = float(cohen_kappa_score(y1, y2))
    return {
        "n": int(len(sub)),
        "agreement": agreement,
        "kappa": kappa,
        "interpretation": interpret_kappa(kappa),
    }


def compute_unanimity(df: pd.DataFrame) -> dict:
    """Triple-judge agreement under binary collapse (C vs not-C)."""
    sub = df.dropna(subset=["haiku_class", "gemini_class", "deepseek_class"])
    h = sub["haiku_class"].apply(is_challenge)
    g = sub["gemini_class"].apply(is_challenge)
    d = sub["deepseek_class"].apply(is_challenge)
    all_c = int((h & g & d).sum())
    all_not = int((~h & ~g & ~d).sum())
    total = int(len(sub))
    split = total - all_c - all_not
    return {
        "n": total,
        "all_challenge": all_c,
        "all_not_challenge": all_not,
        "two_one_split": split,
        "all_disagree_note": (
            "With binary Challenge/not-Challenge collapse, three-way disagreement "
            "is impossible; 2-1 splits cover every non-unanimous case."
        ),
        "pct_unanimous": (all_c + all_not) / total if total else float("nan"),
    }


def compute_fisher(df: pd.DataFrame, judge: str) -> dict:
    """2x2 Fisher's exact: default-challenge vs override × C vs not-C."""
    col = f"{judge}_class"
    default = df[df["bucket"] == "default_challenge"].dropna(subset=[col])
    override = df[df["bucket"] == "override"].dropna(subset=[col])

    a = int(default[col].apply(is_challenge).sum())
    b = int((~default[col].apply(is_challenge)).sum())
    c = int(override[col].apply(is_challenge).sum())
    d = int((~override[col].apply(is_challenge)).sum())

    odds_ratio, p = fisher_exact([[a, b], [c, d]], alternative="two-sided")
    default_tcr = a / (a + b) if (a + b) else float("nan")
    override_tcr = c / (c + d) if (c + d) else float("nan")
    return {
        "table": {
            "default_C": a, "default_notC": b,
            "override_C": c, "override_notC": d,
        },
        "default_tcr": default_tcr,
        "override_tcr": override_tcr,
        "delta": default_tcr - override_tcr,
        "odds_ratio": float(odds_ratio),
        "p_value": float(p),
        "alpha": 0.05,
        "significant": bool(p < 0.05),
        "honest_call": (
            "p < 0.05: significant" if p < 0.05
            else f"p = {p:.4f}: NOT significant at alpha=0.05"
        ),
    }


def per_scenario_distribution(df: pd.DataFrame, judge: str) -> dict:
    col = f"{judge}_class"
    sub = df.dropna(subset=[col]).copy()
    sub["is_c"] = sub[col].apply(is_challenge).astype(int)
    by_scen = sub.groupby("scenario_id")["is_c"].agg(["sum", "count"])
    histogram: Counter = Counter()
    for _, row in by_scen.iterrows():
        histogram[int(row["sum"])] += 1
    return {
        "n_scenarios": int(len(by_scen)),
        "k_to_count": {str(k): int(v) for k, v in sorted(histogram.items())},
        "mean_runs_per_scenario": float(by_scen["count"].mean()) if len(by_scen) else float("nan"),
    }


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    df = build_unified_frame()
    print(f"\nUnified frame: {len(df)} rows")
    print(df.groupby(["bucket"])["key"].count())

    bucket_slices: dict[str, pd.DataFrame] = {
        "default_challenge": df[df["bucket"] == "default_challenge"],
        "override":          df[df["bucket"] == "override"],
        "ctrl_original":     df[df["bucket"] == "ctrl_original"],
        "ctrl_v2":           df[df["bucket"] == "ctrl_v2"],
        "ctrl_combined":     df[df["bucket"].isin(["ctrl_original", "ctrl_v2"])],
    }

    # 1. TCR by condition × judge
    tcr_by_condition = {
        cond: {j: compute_tcr(sub, j) for j in JUDGES}
        for cond, sub in bucket_slices.items()
    }

    # 2. Pairwise kappa across slices
    existing_800 = df[df["bucket"].isin(["default_challenge", "override", "ctrl_original"])]
    new_ctrl_200 = df[df["bucket"] == "ctrl_v2"]

    kappa_slices = [
        ("existing_800", existing_800),
        ("new_ctrl_200", new_ctrl_200),
        ("combined_1000", df),
        ("default_600", bucket_slices["default_challenge"]),
        ("override_150", bucket_slices["override"]),
        ("ctrl_combined_250", bucket_slices["ctrl_combined"]),
    ]
    pairs = [("haiku", "gemini"), ("haiku", "deepseek"), ("gemini", "deepseek")]
    kappa_pairwise: dict = {}
    for slice_name, slice_df in kappa_slices:
        kappa_pairwise[slice_name] = {
            f"{a}_vs_{b}": compute_kappa(slice_df, a, b) for a, b in pairs
        }

    # 3. Per-scenario distribution
    per_scenario = {
        cond: {j: per_scenario_distribution(sub, j) for j in JUDGES}
        for cond, sub in bucket_slices.items()
    }

    # 4. Fisher exact (default-challenge vs override) per judge
    fisher_results = {j: compute_fisher(df, j) for j in JUDGES}

    # 5. IRR summary table
    irr_table: list[dict] = []
    for slice_name, results in kappa_pairwise.items():
        for pair_name, st in results.items():
            agree = st["agreement"]
            kappa = st["kappa"]
            irr_table.append({
                "slice": slice_name,
                "pair": pair_name,
                "n": st["n"],
                "pct_agreement": round(agree * 100, 2) if agree == agree else None,
                "cohen_kappa":   round(kappa, 4)      if kappa == kappa else None,
                "interpretation": st["interpretation"],
            })

    # 6. Triple-judge unanimity
    triple = {
        "combined_1000":      compute_unanimity(df),
        "existing_800":       compute_unanimity(existing_800),
        "new_ctrl_200":       compute_unanimity(new_ctrl_200),
        "default_600":        compute_unanimity(bucket_slices["default_challenge"]),
        "override_150":       compute_unanimity(bucket_slices["override"]),
        "ctrl_combined_250":  compute_unanimity(bucket_slices["ctrl_combined"]),
    }

    out = {
        "meta": {
            "n_total": int(len(df)),
            "n_default_challenge": int(len(bucket_slices["default_challenge"])),
            "n_override":          int(len(bucket_slices["override"])),
            "n_ctrl_original":     int(len(bucket_slices["ctrl_original"])),
            "n_ctrl_v2":           int(len(bucket_slices["ctrl_v2"])),
            "n_ctrl_combined":     int(len(bucket_slices["ctrl_combined"])),
            "judges": JUDGES,
            "binary_collapse": "C -> Challenge; S/O -> not-Challenge",
            "kappa_bands": "Landis & Koch (1977)",
        },
        "tcr_by_condition": tcr_by_condition,
        "kappa_pairwise": kappa_pairwise,
        "per_scenario_distribution": per_scenario,
        "fisher_default_vs_override": fisher_results,
        "irr_summary_table": irr_table,
        "triple_agreement": triple,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as fp:
        json.dump(out, fp, indent=2)
    print(f"\nSaved {out_path}")

    print_summary(out)


def fmt_ci(s: dict) -> str:
    return (
        f"{s['tcr']*100:5.1f}%  "
        f"[{s['wilson_ci_lo']*100:5.1f}, {s['wilson_ci_hi']*100:5.1f}]  "
        f"(n={s['n']})"
    )


def print_summary(out: dict) -> None:
    print("\n" + "=" * 78)
    print("TCCB BENCHMARK — ANALYSIS SUMMARY")
    print("=" * 78)

    print(f"\nTotal unified responses: {out['meta']['n_total']}")
    for k in ("n_default_challenge", "n_override", "n_ctrl_original", "n_ctrl_v2", "n_ctrl_combined"):
        print(f"  {k:25s}: {out['meta'][k]}")

    print("\n--- 1. TCR by condition (Wilson 95% CI) ---")
    for cond, by_judge in out["tcr_by_condition"].items():
        for judge, stats_ in by_judge.items():
            print(f"  {cond:20s} {judge:10s} {fmt_ci(stats_)}")
        print()

    print("--- 2. Pairwise Cohen's kappa ---")
    for slice_name, results in out["kappa_pairwise"].items():
        print(f"  [{slice_name}]")
        for pair, st in results.items():
            print(
                f"    {pair:25s} n={st['n']:4d}  agree={st['agreement']*100:5.1f}%  "
                f"kappa={st['kappa']:+.3f}  {st['interpretation']}"
            )

    print("\n--- 3. Fisher exact: default vs override ---")
    for judge, fr in out["fisher_default_vs_override"].items():
        print(
            f"  {judge:10s} default_TCR={fr['default_tcr']*100:5.1f}%  "
            f"override_TCR={fr['override_tcr']*100:5.1f}%  "
            f"delta={fr['delta']*100:+5.1f} pp  "
            f"OR={fr['odds_ratio']:.2f}  p={fr['p_value']:.4f}  -> {fr['honest_call']}"
        )

    print("\n--- 4. Triple-judge unanimity ---")
    for slice_name, t in out["triple_agreement"].items():
        print(
            f"  [{slice_name}] n={t['n']}  all_C={t['all_challenge']}  "
            f"all_notC={t['all_not_challenge']}  2-1_split={t['two_one_split']}  "
            f"unanimous={t['pct_unanimous']*100:.1f}%"
        )
    print("=" * 78)


if __name__ == "__main__":
    main()
