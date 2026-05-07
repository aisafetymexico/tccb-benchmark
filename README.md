# TCCB v1.0: Therapeutic Challenge Competence Benchmark

A skill-specific calibration benchmark for one therapeutic intervention — Hill's *Challenge* (Helping Skills System Category 6) — measuring whether large language models deploy the skill in clinically appropriate contexts and avoid it where empathic validation is indicated.

## What is this?

TCCB is a public benchmark that pairs 170 single-turn clinical scenarios with a cross-family LLM judging protocol to evaluate *calibration* of a single therapeutic skill, not therapeutic alliance or quality. Scenarios are grounded in Hill's Helping Skills System (HSS); ground truth is anchored in scenario condition labels (Challenge-prescribed vs. validation-appropriate) and Hill's six Web Form E worked examples used for judge calibration. The benchmark accompanies the ICAIMH 2026 paper *Token Mimicry or Therapeutic Competence? Testing LLMs Against Hill's Challenge Skill in Mental Health Support Scenarios*.

## Quick stats

- **170 scenarios** — 120 Challenge-prescribed (4 thematic clusters of 30) + 50 validation-appropriate control
- **1,000 subject-model responses** — 5 runs × 200 (scenario × condition) cells, on `claude-opus-4-6`
- **3,000 judgments** — 3 cross-family LLM judges (Claude Haiku, Gemini 2.5 Flash, DeepSeek-Chat)
- **Calibration**: Hill's 6 Web Form E worked examples; Haiku 6/6, Gemini 6/6, DeepSeek 5/6
- **Licenses**: code MIT; data and benchmark CC-BY-4.0

## Repository structure

```
tccb-benchmark/
├── benchmark/              # the 170 scenarios with marker annotations and ground-truth labels
│   ├── challenge_scenarios/    # 120 Challenge-prescribed (clusters A–D, 30 each)
│   └── control_scenarios/      # 50 validation-appropriate controls (CTRL-01 … CTRL-50)
├── prompts/                # subject system prompt, override prompt, judge system prompt + user template
├── data/
│   ├── responses/              # 1,000 subject-model responses (per scenario × condition × run)
│   └── judgments/{haiku,gemini,deepseek}/  # 3,000 per-response classifications
├── results/                # aggregated TCR, κ, calibration, figures (PDF + PNG)
│   ├── results.json
│   ├── calibration.json
│   └── figures/
├── analysis/               # Python analysis pipeline (recompute everything from data/)
├── docs/                   # full documentation, methodology, citation formats
├── CITATION.cff
├── LICENSE                 # MIT — applies to analysis/ code
├── LICENSE-DATA            # CC-BY-4.0 — applies to benchmark/, data/, results/
├── VERSION
└── README.md
```

## Quickstart — Reproducing the analysis

```bash
cd analysis
pip install -r requirements.txt
python analyze.py        # recomputes TCR + Wilson CIs + Cohen's κ from data/
python make_figures.py   # regenerates fig1 (TCR by judge) and fig2 (per-scenario distribution)
```

Outputs land in `results/` and `results/figures/`. Provider aliases (`gemini-2.5-flash`, `deepseek-chat`) can drift; exact replication of the judging step requires the model identifiers listed in `docs/full_documentation.md`.

## Citation

```bibtex
@inproceedings{pineloHau2026tccb,
  author    = {Pinelo Hau, Jason Maximiliano},
  title     = {Token Mimicry or Therapeutic Competence? Testing LLMs Against
               Hill's Challenge Skill in Mental Health Support Scenarios},
  booktitle = {Proceedings of the International Conference on Artificial
               Intelligence for Mental Health (ICAIMH 2026)},
  series    = {Communications in Computer and Information Science},
  publisher = {Springer},
  address   = {M\'erida, M\'exico},
  year      = {2026},
  month     = jul,
  note      = {Therapeutic Challenge Competence Benchmark (TCCB) v1.0}
}
```

Plain text:
> Pinelo Hau, J. M. (2026). *Token Mimicry or Therapeutic Competence? Testing LLMs Against Hill's Challenge Skill in Mental Health Support Scenarios.* Proceedings of the International Conference on Artificial Intelligence for Mental Health (ICAIMH 2026), Mérida, México, July 1–3, 2026. Springer CCIS.

Additional citation formats (APA, IEEE, ACM, dataset-only, code-only) are in `docs/citation.md`.

## Licenses

- **Code** (`analysis/`): MIT — see [`LICENSE`](LICENSE)
- **Data and benchmark** (`benchmark/`, `data/`, `results/`, `prompts/`): Creative Commons Attribution 4.0 International (CC-BY-4.0) — see [`LICENSE-DATA`](LICENSE-DATA)

If you reuse TCCB scenarios or judgments, attribution is required under CC-BY-4.0. Please cite the paper above.

## Contact

Jason Maximiliano Pinelo Hau — `mpinelo@aismx.org`
AI Safety México, Mérida, México
ORCID: [0009-0003-0779-4333](https://orcid.org/0009-0003-0779-4333)

