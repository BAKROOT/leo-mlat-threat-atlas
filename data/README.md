# Data

One workbook is the master copy: `catalogue/LEO_MLAT_Threat_Catalogue.xlsx` (release v1.8). It holds the extended threat catalogue and the evidence atlas it is built on (sheets below).
Plain-text snapshots of its data sheets are in `catalogue/csv/` (catalogue sheets) and `atlas/csv/` (atlas sheets); `python scripts/export_csv.py` regenerates them.
Values in the CSV files are the cached values stored in the workbook.

## `catalogue/LEO_MLAT_Threat_Catalogue.xlsx`

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
| Worked | the worked displacement application (Table 4 of the paper) recomputed from the Catalogue | `worked_example.csv` |
| Checks | every statistic the paper states about the catalogue, recomputed (117 rows, all OK) | `paper_statistics_checks.csv` |
| Review | mistakes found in the earlier SATERA workbook and the correction made | `review_of_earlier_workbook.csv` |
| CVE Register | the 57 CVE records of the atlas, mapped to assets and threats | `cve_register_57.csv` |
| Threat Propagation | one row per threat and asset it names (65 rows): route to the ATM system, assets reached, boundaries | `threat_propagation_65.csv` |
| Asset-Threat Matrix | the 27 assets against the 55 threats (main, other, reachable) | `asset_threat_matrix.csv` |
| Asset Connections | what each asset receives from and feeds, with the kind of link | `asset_connections_27.csv` |
| Multi-step Attacks | 20 multi-step attacks, incidents and analogues from the atlas, with steps, layers and the threats they support | `multistep_attacks.csv` |
| Mitigations | the 25 defences M01 to M25 and how many threats cite each | `mitigations_25.csv` |
| Dashboard, L1 to L4, Legends, Dashboard Data | summary, live per-layer views, definitions and the formulas that feed the dashboard | |
| Atlas sheets (8) | the evidence atlas, described in the next section | `../atlas/csv/` |

**Version.** Release v1.8 (5 November 2026), the final catalogue and the only version kept: the file is `LEO_MLAT_Threat_Catalogue.xlsx`, without a version number in its name, so that no earlier version can be mistaken for it.
It holds the 55 threats (T1.01 to T4.15) with the scores and ratings of release v1.3 (30 October 2026); v1.4 to v1.7 add the layout, the dashboard, the sheets Threat Propagation, Asset-Threat Matrix,
Asset Connections, Multi-step Attacks and Mitigations, and further checks; v1.8 merges the evidence atlas into the same file (below) without changing any value. The panel analysis gives identical results on it. The co-author evaluation is **yet to be done**.
The change log is in the workbook's sheet *README & Change Log*; earlier working versions were removed and survive only in the git history.

**Validation status.** Every record was reviewed by a blind four-model LLM panel (`llm_panel/`); the evaluation by the co-authors is **yet to be done**. The
scores and the scoring algorithms were verified (sheet *Checks*, `make check`). The column *Review status* separates 7 *Baseline* records,
which reproduce the values printed in Table 4 of the paper (five source threats and two enablers), from 48 *Panel-reviewed* records, which carry
the same panel review but are not printed in the paper's tables. For the latter, the paper fixes the statistics and the identifiers.

**The 17-entry catalogue.** Sheet *SATERA* holds the SATERA project's earlier asset-level catalogue (entries SC-1 to SC-17) with numeric
DREAD scores, register asset IDs and corrected PASTA stages. The extended catalogue refines it: 44 of the 55 threats refine at least one
entry (column *SATERA entries refined*) and 11 are new. The sheet *Review* lists the defects corrected in the earlier workbook.

**Scores.** Ordinal analyst derivations, not rater consensus and not probabilities. R comes from the best bound evidence (one level less if the
evidence is from an analogue system only), E from the adversary tier, D from the goals served (and Affected users), A and Di are analyst inputs
read from the attack graph, S = D+R+E+A+Di, and the bands are Low 5 to 9, Medium 10 to 14, High 15 to 19, Critical 20 to 25.
Di (and S) are given for a strong and a weak geometric pass. `scripts/check_paper_counts.py` recomputes R, E, D, S and the band for every threat.

## Atlas sheets of the same workbook (`atlas/csv/`)

The evidence base behind the catalogue: 78 published sources coded by layer entered, layer affected, direction, boundaries crossed,
timing dependency, evidence level (E0 analytical, E1 simulation or recorded data, E2 real hardware, E3 operational system), peer-review
status and verified link (checked 13 October 2026), plus 57 CVEs and 25 mitigations. Until release v1.7 the atlas was a second workbook
(`PRISM-LEO_Threat_Exploit_Atlas.xlsx`); v1.8 merged it in. The atlas sheets *CVE Register* and *Mitigations* were not copied again: the catalogue's
sheets of the same name already hold every atlas column (same values) and the atlas formulas now read them.

| Sheet | Content | CSV |
|---|---|---|
| Atlas Overview | live summary of the atlas (entries, peer-reviewed share, CVEs, mitigations, evidence levels), with checks | `atlas/csv/overview_raw.csv` |
| Threat Atlas | 78 sources, 40 columns, numbered #1 to #78 (the numbers are stable; new sources get new numbers) | `atlas/csv/atlas_78_sources.csv` |
| Asset Evidence | the 27 assets with L3 assets, atlas sources and CVEs mapped to each, and propagation | `atlas/csv/asset_evidence_27.csv` |
| CVE Register | 57 CVE records, each confirmed as published (catalogue sheet, listed above) | `catalogue/csv/cve_register_57.csv` |
| Mitigations | 25 standards, regulations and guidance documents (catalogue sheet, listed above) | `catalogue/csv/mitigations_25.csv` |
| Gap Matrix | live counts of atlas entries by layer and attack category; zero cells are gaps no source covers | `atlas/csv/gap_matrix_raw.csv` |
| Paper Alignment | one row per study of the comparative review of the paper (Section 2) | `atlas/csv/paper_alignment.csv` |
| Classification Key | how each column was classified | `atlas/csv/classification_key_raw.csv` |
| Excluded Entries | bibliography entries not carried in the review table (for example grey literature without a stable link) and the reason | `atlas/csv/excluded_entries_raw.csv` |
| Atlas Summary | exploitation status of the original 43-paper review set | |

The atlas holds high-level summaries only: no parameters, procedures or tooling.

## `derived/`

`asset_reach.csv`: for each asset, the number of other assets and layers an effect can reach, read from the *Assets* sheet
(`python scripts/asset_reach.py`).

## Notes

* The edge register of the asset dependency graph (40 edges of four kinds: 15 data, 5 timing, 6 control, 14 hosting) is `derived/edge_provenance.csv`
  (source, kind, provenance status: stated, inferred or author reading, boundaries crossed); `derived/graph_sensitivity.csv` gives the results under subsets of the edges;
  `derived/preconditions.csv` gives class, tier, evidence status and enabler per threat. Regenerate with `python graph/graph.py`.
