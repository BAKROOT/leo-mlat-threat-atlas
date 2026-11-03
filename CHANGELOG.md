# Changelog

## Unreleased

* **Catalogue v1.7 is now the only catalogue.** `data/catalogue/LEO_MLAT_Threat_Catalogue.xlsx` replaces `SATERA_Extended_Threat_Catalogue.xlsx` (release v1.3). The new file has no version
  number in its name so that no earlier version can be mistaken for it. Scores and ratings are those of v1.3 (the checks, the panel analysis and the prompts rebuild all give identical results);
  v1.4 to v1.7 add the README with change log, the dashboard, four layer views and the sheets Threat Propagation, Asset-Threat Matrix, Asset Connections, Multi-step Attacks and Mitigations.
* `scripts/export_csv.py` exports the five new sheets to `data/catalogue/csv/`; the Checks sheet now has 117 rows (was 112), all OK; `scripts/check_paper_counts.py` expects 117.
* `docs/METHOD.md`, `docs/LIMITATIONS.md`, `data/README.md`, `docs/DATA_DICTIONARY.md` and `README.md` describe the framing used in the paper: PASTA unchanged, STRIDE-tau extends STRIDE,
  PA-DREAD adapts DREAD (Discoverability = detection depth).

* Wording only: the catalogue is no longer described as evaluated by the co-authors. That evaluation is **yet to be done** and will follow completion of the paper;
  the *Review status* label of the 48 extended records is now *Panel-reviewed: co-author evaluation yet to be done*. No score, formula or data value changed.

## 1.0.0 (30 October 2026)

First public release, matching the manuscript version with 55 threats.

* `data/catalogue`: SATERA Extended Threat Catalogue, release v1.3 (55 threats, T1.01 to T4.15; CVE register sheet, related-CVE and
  propagation columns). Reviewed by the multi-vendor LLM panel; the evaluation by the co-authors is yet to be done; scores and algorithms verified.
  Relative to the working file v1.2 only wording changed: the *Review status* labels (*Panel-reviewed* instead of the working label), the
  README, Review and Legends sheets, and section references. No score, formula or data value changed.
* `data/atlas`: PRISM-LEO Threat and Exploit Atlas, final release (78 sources, 57 CVEs, 25 mitigations, asset register with the L3 assets).
* `llm_panel`: blind review of the 55 threats by four models from four vendors (Claude Sonnet 5.5, ChatGPT GPT-6, DeepSeek DeepThink,
  Gemini 3.1 Pro): prompts, replies, merged ratings, agreement and disagreement analysis, completeness mapping, test-retest and figures.
  The ChatGPT seat was re-run with the full prompts on 29 October 2026 so that all four models received byte-identical text;
  the earlier ChatGPT run (14 small prompt parts) is kept in `llm_panel/sensitivity/`.
* `scripts`, `tests`, `Makefile`: checks of the paper's counts and scores against the workbooks, reproduction of the panel analysis.

Not in this release: the dependency-graph edge list (see `docs/LIMITATIONS.md`).
