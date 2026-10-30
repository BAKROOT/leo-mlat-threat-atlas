# Changelog

## 1.0.0 (30 October 2026)

First public release, matching the manuscript version with 55 threats.

* `data/catalogue`: SATERA Extended Threat Catalogue, final release v1.3 (55 threats, T1.01 to T4.15; CVE register sheet, related-CVE and
  propagation columns). Validated by the multi-vendor LLM panel and evaluated by the co-authors; scores and algorithms verified.
  Relative to the working file v1.2 only wording changed: the *Review status* labels (*Validated* instead of the working label), the
  README, Review and Legends sheets, and section references. No score, formula or data value changed.
* `data/atlas`: PRISM-LEO Threat and Exploit Atlas, final release (78 sources, 57 CVEs, 25 mitigations, asset register with the L3 assets).
* `llm_panel`: blind review of the 55 threats by four models from four vendors (Claude Sonnet 5.5, ChatGPT GPT-6, DeepSeek DeepThink,
  Gemini 3.1 Pro): prompts, replies, merged ratings, agreement and disagreement analysis, completeness mapping, test-retest and figures.
  The ChatGPT seat was re-run with the full prompts on 29 October 2026 so that all four models received byte-identical text;
  the earlier ChatGPT run (14 small prompt parts) is kept in `llm_panel/sensitivity/`.
* `scripts`, `tests`, `Makefile`: checks of the paper's counts and scores against the workbooks, reproduction of the panel analysis.

Not in this release: the dependency-graph edge list (see `docs/LIMITATIONS.md`).
