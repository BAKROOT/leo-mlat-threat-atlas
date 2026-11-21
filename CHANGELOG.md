# Changelog

## Unreleased (after 2.1.0)

* **Workbook text and numbers aligned with the paper (file name and version unchanged).** The exploitability tier T3x reads "T3 plus a second class" in the sheets Rubric, Legends and Dashboard Data (the prompts in `llm_panel/` keep the wording the models were shown). The sheet Geometry Gains, sections B and C, now holds the results of the RAIM-style monitor (`geometry/raim_results.json`) that the paper reports in its stealth-window table, in place of the earlier model; the description in A2 and the note are updated. The column *Paper location* of the sheet Checks no longer cites workbook versions: it gives the paper section, or "Workbook only (not stated in the paper)". The csv snapshots are regenerated. No score, rating, count or formula result of the catalogue changed (`make check`: 117 checks pass).

* **Literature search record (`data/search/`).** The search behind the 41 security studies of the synthesis was re-run on 21 November 2026 and logged: the exact strings per database, 3,524 records retrieved, 1,047 duplicates removed, 2,477 unique records, and the coverage of the 41 studies (23 retrieved; the reason for each of the 18 that were not). The 41 studies were selected for relevance by one author from an earlier search that was not logged, so the re-run is a coverage check. The raw exports are not redistributed. No catalogue entry, score or count changed.

## 2.1.0 (21 November 2026), accompanies the submitted manuscript

* **Integrity model of the stealth window.** `geometry/raim.py` assumes the textbook least-squares residual (chi-square) test of RAIM (Brown 1992), with P_FA = P_MD = 1e-3 and range error sigma = 10, 30, 100 m, and computes per satellite the minimum detectable bias, the slope and the protection level. The stealth window is the intersection of the L1 window (bias that passes the clock checks; eps_L1 = 30 m, the covert 100 ns step of assumption W1) and the L3 window [e_req/g_i, MDB_i). Results (`raim_results.json`) for variants A-D and for T2.04 leaving 6, 4 or 3 reports: in the nominal 10x20 variant the clock route never opens (g_max <= 0.79, so the 30 m step gives at most 24 m), whereas after T2.04 it opens in at least 4, 32 and 54 % of the samples. The model is an assumption: the SATERA monitor is not published.
* `geometry/README.md` lists `raim.py`.
* **End-to-end simulation (`simulation/`).** An assumed SATERA-like testbed: nonlinear multilateration with a residual monitor, an ADS-B cross-check, a reconstructed onboard clock filter (GNSS + PTP with innovation, consistency and drift-compliance checks), attack chains over 10-min flights and two defences (protection-level alarm D1, dropped-report monitor D2). Results: the analytic window predicts the simulated probability of an undetected breach within 0.006 on average (0.02 after T2.04); a single biased clock input induces under 1 m without a clock alarm, both inputs together 31 m; the clock bias of W1 displaces a target undetected only with T2.04 (0.5 % of seconds with 4 reports, 22 % with 3); D1 flags all of these and D2 detects T2.04 within 1 to 3 s; a per-satellite clock state absorbs a 300 m step to 21 m within 60 s. `make simulate` reruns geometry and simulation; a `Dockerfile` reproduces everything.
* **Workbook v2.0 in the repository.** `data/catalogue/LEO_MLAT_Threat_Catalogue_v2_0.xlsx` (the file the paper names) replaces the v1.8 copy `LEO_MLAT_Threat_Catalogue.xlsx`; every script, test and README now points to it. The CSV snapshots are re-exported: no value of the catalogue changed (`catalogue_55_threats.csv` is identical); `asset_evidence_27.csv` is removed because the sheet was merged into Assets (columns Q to S); `geometry_gains_raw.csv` and `direct_vs_enabled_raw.csv` are added. `make check` (388 of 388), `make panel` (identical) and `pytest` (9 passed) pass on the new file.

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
