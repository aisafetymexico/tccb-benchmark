# TCCB v1.0 — Citation formats

This document provides copy-pasteable citation formats for the TCCB benchmark and the accompanying ICAIMH 2026 paper.

The **canonical citation** is the paper. Cite the paper whenever you use the benchmark, the released responses, or the released judgments. If you fork or extend the analysis code, additionally cite the repository with the version pin from `VERSION`.

If a Zenodo DOI is later minted for the dataset and/or repository, append it to the relevant citation alongside the paper.

---

## 1. Citing the paper (canonical)

### BibTeX

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

### APA (7th edition)

> Pinelo Hau, J. M. (2026). Token mimicry or therapeutic competence? Testing LLMs against Hill's Challenge skill in mental health support scenarios. In *Proceedings of the International Conference on Artificial Intelligence for Mental Health (ICAIMH 2026)* (Communications in Computer and Information Science). Springer.

### IEEE

> J. M. Pinelo Hau, "Token Mimicry or Therapeutic Competence? Testing LLMs Against Hill's Challenge Skill in Mental Health Support Scenarios," in *Proc. Int. Conf. Artificial Intelligence for Mental Health (ICAIMH 2026)*, Mérida, México, Jul. 2026, ser. Communications in Computer and Information Science. Springer.

### ACM

> Jason Maximiliano Pinelo Hau. 2026. Token Mimicry or Therapeutic Competence? Testing LLMs Against Hill's Challenge Skill in Mental Health Support Scenarios. In *Proceedings of the International Conference on Artificial Intelligence for Mental Health (ICAIMH 2026)* (Communications in Computer and Information Science). Springer, Mérida, México.

### Plain text (informal)

> Pinelo Hau, J. M. (2026). *Token Mimicry or Therapeutic Competence? Testing LLMs Against Hill's Challenge Skill in Mental Health Support Scenarios.* ICAIMH 2026, Mérida, México, July 1–3, 2026. Springer CCIS.

---

## 2. Citing the benchmark / dataset only

When you use the **scenarios, subject responses, or judgments** as data — for example, to train a probe, validate a different judge, or replicate a result — cite the paper as the canonical source and additionally identify the dataset version.

### BibTeX

```bibtex
@misc{pineloHau2026tccbDataset,
  author       = {Pinelo Hau, Jason Maximiliano},
  title        = {Therapeutic Challenge Competence Benchmark (TCCB), v1.0},
  year         = {2026},
  howpublished = {\url{https://github.com/aisafetymexico/tccb-benchmark}},
  note         = {Companion dataset to Pinelo Hau (2026), ICAIMH 2026.
                  Released CC-BY-4.0.}
}
```

### Plain text

> Pinelo Hau, J. M. (2026). *Therapeutic Challenge Competence Benchmark (TCCB), v1.0* [Dataset]. AI Safety México. https://github.com/aisafetymexico/tccb-benchmark. Companion dataset to Pinelo Hau (2026), ICAIMH 2026. Released under CC-BY-4.0.

---

## 3. Citing the analysis code only

When you fork or extend the **Python analysis pipeline** (`analysis/`), cite the paper and the repository version.

### BibTeX

```bibtex
@software{pineloHau2026tccbCode,
  author       = {Pinelo Hau, Jason Maximiliano},
  title        = {TCCB analysis pipeline (v1.0.0)},
  year         = {2026},
  howpublished = {\url{https://github.com/aisafetymexico/tccb-benchmark}},
  note         = {MIT-licensed analysis code accompanying the
                  Therapeutic Challenge Competence Benchmark.}
}
```

### Plain text

> Pinelo Hau, J. M. (2026). *TCCB analysis pipeline* (Version 1.0.0) [Software]. AI Safety México. https://github.com/aisafetymexico/tccb-benchmark. Released under the MIT License.

---

## 4. CITATION.cff

The repository ships a `CITATION.cff` file at the repository root, in the [Citation File Format v1.2.0](https://citation-file-format.github.io/) schema. GitHub's "Cite this repository" button reads this file and produces APA / BibTeX exports automatically. The `preferred-citation` block in `CITATION.cff` corresponds to §1 of this document.

---

## 5. Notes on attribution

- **CC-BY-4.0** (`benchmark/`, `prompts/`, `data/`, `results/`) requires giving appropriate credit, providing a link to the license, and indicating any changes made. The paper citation in §1 above satisfies the credit requirement; the link to the license should point to <https://creativecommons.org/licenses/by/4.0/>.
- **MIT** (`analysis/`) requires only the standard copyright notice in `LICENSE` to be retained in derivative works.
- If you use TCCB in a paper, please **also cite the foundational frameworks** TCCB rests on, in particular Hill (2020) for the Helping Skills System and Sharma et al. (2024) for sycophancy in RLHF preference models. The full reference list is in the bibliography of the ICAIMH 2026 paper.
