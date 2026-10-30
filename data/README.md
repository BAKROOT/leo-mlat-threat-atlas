# Data

Two workbooks are the master copies. Each has a `csv/` folder with a plain-text snapshot of its data sheets
(`python scripts/export_csv.py` regenerates them). Values in the CSV files are the cached values stored in the workbooks.

## `catalogue/SATERA_Extended_Threat_Catalogue.xlsx`

The 55-threat catalogue of the paper. Built from the 17-entry SATERA catalogue with STRIDE-tau (enumeration), PASTA (process),
effect-transfer graphs (propagation) and propagation-aware DREAD (ranking). Blue text marks analyst input, black marks formulas.

| Sheet | Content | CSV |
|---|---|---|
| README | purpose, version history, how a score is made, what is not claimed | |
| Catalogue | the 55 threats with scores, reach, evidence, framework mappings (48 columns; [dictionary](../docs/DATA_DICTIONARY.md)) | `catalogue_55_threats.csv` |
| Rubric | lookup tables that drive every score: evidence to R, tier to E, goal to D, score to band | `rubric_raw.csv` |
| Binding | one row per (threat, atlas source): binding type, evidence level, peer-review status, verified link | `threat_x_atlas_source_binding.csv` |
| Assets | the 27-asset register with live threat counts and the cross-layer reach of an attack on each asset | `asset_register_27.csv` |
| SATERA | the earlier 17 entries, corrected and linked to the extended threats | `satera_17_entries.csv` |
| Worked | the worked displacement application (Tables 4 and 5 of the paper) recomputed from the Catalogue | `worked_example.csv` |
| Checks | every statistic the paper states about the catalogue, recomputed (112 rows, all OK) | `paper_statistics_checks.csv` |
| Review | mistakes found in the earlier SATERA workbook and the correction made | `review_of_earlier_workbook.csv` |
| CVE Register | the 57 CVE records of the atlas, mapped to assets and threats | `cve_register_57.csv` |
| Legends | definitions | |

**Version.** Release v1.3 (30 October 2026): the final catalogue of 55 threats (T1.01 to T4.15), validated and evaluated as described
below. Earlier working versions (v1.0 to v1.2) added the CVE Register sheet, the columns *Related CVEs* and *Cross-layer propagation* and
further checks; the panel analysis gives identical results on all of them. Relative to the file supplied for release, v1.3 changes wording only
(the *Review status* labels, the README and Review sheets and the section references); no score, formula or data value changed.

**Validation status.** Every record was validated by a blind four-model LLM panel (`llm_panel/`) and then evaluated by the co-authors; the
scores and the scoring algorithms were verified (sheet *Checks*, `make check`). The column *Review status* separates 7 *Baseline* records,
which reproduce the values printed in Table 5 of the paper (five source threats and two enablers), from 48 *Validated* records, which carry
the same validation but are not printed in the paper's tables. For the latter, the paper fixes the statistics and the identifiers.

**The 17-entry catalogue.** Sheet *SATERA* holds the SATERA project's earlier asset-level catalogue (entries SC-1 to SC-17) with numeric
DREAD scores, register asset IDs and corrected PASTA stages. The extended catalogue refines it: 44 of the 55 threats refine at least one
entry (column *SATERA entries refined*) and 11 are new. The sheet *Review* lists the defects corrected in the earlier workbook.

**Scores.** Ordinal analyst derivations, not rater consensus and not probabilities. R comes from the best bound evidence (one level less if the
evidence is from an analogue system only), E from the adversary tier, D from the goals served (and Affected users), A and Di are analyst inputs
read from the attack graph, S = D+R+E+A+Di, and the bands are Low 5 to 9, Medium 10 to 14, High 15 to 19, Critical 20 to 25.
Di (and S) are given for a strong and a weak geometric pass. `scripts/check_paper_counts.py` recomputes R, E, D, S and the band for every threat.

## `atlas/PRISM-LEO_Threat_Exploit_Atlas.xlsx`

The evidence base behind the catalogue: 78 published sources coded by layer entered, layer affected, direction, boundaries crossed,
timing dependency, evidence level (E0 analytical, E1 simulation or recorded data, E2 real hardware, E3 operational system), peer-review
status and verified link (checked 13 October 2026), plus 57 CVEs and 25 mitigations.

| Sheet | Content | CSV |
|---|---|---|
| Overview | live summary of the atlas (entries, peer-reviewed share, CVEs, mitigations, evidence levels), with checks | `overview_raw.csv` |
| Threat Atlas | 78 sources, 40 columns, numbered #1 to #78 (the numbers are stable; new sources get new numbers) | `atlas_78_sources.csv` |
| Asset Register | the 27 assets with L3 assets, CVE counts and propagation | `asset_register_27.csv` |
| CVE Register | 57 CVE records, each confirmed as published | `cve_register_57.csv` |
| Mitigations | 25 standards, regulations and guidance documents | `mitigations_25.csv` |
| Gap Matrix | live counts of atlas entries by layer and attack category; zero cells are gaps no source covers | `gap_matrix_raw.csv` |
| Paper Alignment | one row per row of Tables 1 to 3 of the paper | `paper_alignment.csv` |
| Classification Key | how each column was classified | `classification_key_raw.csv` |
| Excluded Entries | bibliography entries not carried in the review table (for example grey literature without a stable link) and the reason | `excluded_entries_raw.csv` |
| Summary | exploitation status of the original 43-paper review set | |

The atlas holds high-level summaries only: no parameters, procedures or tooling.

## `derived/`

`asset_reach.csv`: for each asset, the number of other assets and layers an effect can reach, read from the *Assets* sheet
(`python scripts/asset_reach.py`).

## Notes

* The edge list of the asset dependency graph (41 edges of four kinds: 15 data, 5 timing, 7 control, 14 hosting) is not part of these
  workbooks, so the radius, fan-in and rank-correlation statistics of Section 6 of the paper are not reproduced from this release.
  `scripts/asset_reach.py` works from the reach lists stored in the *Assets* sheet.
