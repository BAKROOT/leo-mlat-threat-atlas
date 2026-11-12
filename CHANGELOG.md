# Changelog

## 2.0.0 (12 November 2026), aligned with manuscript version 2.0 (pre-submission revision)

Workbook version 2.0 (`LEO_MLAT_Threat_Catalogue_v2_0`) corresponds to this release and to the manuscript with the supplementary section *Clarifications, Sensitivity Analyses and Reproducibility Details*.

* **Dependency graph resolved at 40 edges.** `graph/graph.py` writes `graph_edges.csv` (= `data/derived/edge_provenance.csv`: 40 edges, source, kind, status stated / inferred / author reading, boundaries crossed) and `graph_results.json`. The manuscript now counts 40 (15 data, 5 timing, 6 control, 14 hosting); the 41st edge of earlier drafts could not be recovered and no candidate edge changes any reported value. `data/derived/graph_sensitivity.csv` gives the results with data and timing only; plus control; all four types; without the inferred S1 and S2; and with A4.7 split into operators and suppliers.
* **Geometry.** `geometry/` holds the scripts, parameters and results of the per-satellite gain (e_h = g_i * eps, g_i <= HDOP), the actual horizontal error of the covert step, the stealth window with a residual test, the transfer channel C (threshold relaxation k = 1, 2, 4) and dropped reports. h* = 350/30 = 11.7 is a necessary-condition screening threshold. Results reproduce exactly.
* **Preconditions and evidence.** `data/derived/preconditions.csv`: class, class entry point, tier, assets, trust boundary, evidence status (direct 8, analogue only 31, postulated 16), enabler for a strong pass. Workbook sheets *Preconditions* and *Direct vs Enabled*; CVE Register columns AA to AC give the mapping type (source-disclosed 51, related surface 4, architectural analogy 2) and confidence.
* **Validation protocol.** `validation/`: stratified 20-threat sample (seed 20261112), rating form, Krippendorff's alpha with bootstrap intervals (checked against the `krippendorff` package). The human study has **not** been run.
* `docs/DECISION_RULES.md`: PA-DREAD scope, STRIDE-tau rules, authentication-invariance test, PASTA traceability and graph semantics.
* `scripts/score_sensitivity.py` (one-point sensitivity of the PA-DREAD totals) takes the catalogue path as an argument.
* Workbook: Paper Alignment *Ref.* column follows the numbering of the current manuscript; the published chains of Multi-step Attacks are labelled MS1 to MS20 so that they do not clash with the manuscript chains C1 to C6; README "Not claimed" states the 40-edge register.
* Docs: `docs/LIMITATIONS.md`, `README.md` and `data/README.md` describe the 40-edge register. No score, rating or count of the catalogue changed.
* Not done: the DOI (to be minted for the submission release), the human expert study, and re-export of `data/catalogue/LEO_MLAT_Threat_Catalogue.xlsx` from the v2.0 Google Sheet (the workbook in this folder is still v1.8 and lacks the new sheets; the new tables are in `data/derived/`).

## 1.1.0 (5 November 2026)

* Consistency pass over the atlas sheets: the BibTeX key of atlas source #20 (Senn et al., WiSec 2025) is now `Senn2025MLATSpoofing`, the key the paper cites (it was `Senn2025UniversalMLAT` and marked "not yet in .bib");
  the sheets *Paper Alignment* and *Classification Key* state that their Table, figure and section numbers refer to the earlier TDSC draft (in the current paper the 41-study synthesis is Section 2.3, Fig. 1);
  drafting leftovers ("your bibliography", "your threat model") reworded. No count, score or formula result changed.
* **One workbook instead of two.** The PRISM-LEO Threat and Exploit Atlas workbook is merged into `data/catalogue/LEO_MLAT_Threat_Catalogue.xlsx`, which is now release v1.8 (30 sheets: the 22 catalogue
  sheets unchanged plus Atlas Overview, Threat Atlas, Asset Evidence, Gap Matrix, Paper Alignment, Atlas Summary, Classification Key and Excluded Entries). The atlas sheets *CVE Register* and *Mitigations*
  are not duplicated: the catalogue versions already held every atlas column with identical values, and the atlas formulas now read them. All 4,640 formulas recalculate to the values of the two
  source workbooks (every cell compared); the Checks sheet still reads 117 of 117 OK. `data/atlas/PRISM-LEO_Threat_Exploit_Atlas.xlsx` and the two atlas CSV copies of *CVE Register* and
  *Mitigations* are removed (the catalogue CSVs hold them); `data/atlas/csv/asset_register_27.csv` is renamed `asset_evidence_27.csv`. `scripts/export_csv.py` and
  `scripts/check_paper_counts.py` read the single workbook; `make check` (388 checks), `make test` and the prompts rebuild give identical results.
* **Aligned with the audited paper.** Section, figure and table numbers in the README and docs now follow the paper (panel Sec. 4.10 and Table 5; cross-layer analysis Sec. 5; worked table Table 4).
* `scripts/asset_reach.py` now also reproduces the fan-in of the processing assets (21, 22, 22, 24) and the Spearman correlation between radius and threat count (0.22, p = 0.26; the paper
  corrected its earlier value of 0.12). The 40 edges of the *Asset Connections* sheet reproduce all 27 reach lists exactly; the paper's 41st edge is still to be recovered (docs/LIMITATIONS.md).

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
