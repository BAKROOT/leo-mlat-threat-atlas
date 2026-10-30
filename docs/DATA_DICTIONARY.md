# Data dictionary

## Catalogue workbook, sheet *Catalogue* (`catalogue_55_threats.csv`), one row per threat

| Column | Meaning |
|---|---|
| ID | `T<layer>.<nn>`: threat T1.01 to T4.15; stable identifiers used in the paper |
| Layer | L1 to L4 |
| Threat | short title |
| Description (mechanism level) | what happens, at the level of mechanisms; no parameters, procedures or tooling |
| Attack vector | how the threat is brought to bear, at a high level |
| Asset(s) | asset ID(s) of the 27-asset register, e.g. A1.1, A3.4 |
| Trust boundary | TB0 to TB3 where the threat sits or which it crosses |
| STRIDE-tau primary / Secondary | category codes S, T, R, I, D, E, tau (see [METHOD.md](METHOD.md)); up to two secondary |
| Authentication-invariance test / tau note | result of the test that separates tau from Tampering |
| Timing relation | `Target` (the threat targets the time reference) or `Derived` (it acts on timing-derived data); empty if not on the timing dependency |
| Adversary class | AC1 to AC7 |
| Tier code | T1p, T1c, T2, T3, T3x |
| Displacement, Denial, Deception, Disclosure | goal flags (`Y` where served); *Goals (n)* counts them |
| Role | `Leaf` (a threat with a consequence of its own) or `Enabler` (completes other chains; no D) |
| Evidence | highest level among the bound atlas sources: P, E0, E1, E2, E3 |
| Analogue only | `Y` if all evidence is from another system (R is reduced by one level) |
| Support not peer-reviewed | `Yes` if the supporting sources are not peer-reviewed |
| Bound atlas sources (#) | atlas source numbers (sheet *Binding* has one row per threat and source) |
| Path evidence (#) | atlas source numbers that support the propagation path rather than the attack (binding type `Path`) |
| Mitigation IDs | mitigation IDs of the bound sources (atlas sheet *Mitigations*) |
| rho_det, rho_root | propagation reach: layer steps along the shortest path to the first integrity check (A3.4 or A3.5) and to the ATM picture (A4.6) |
| D, R, E, A | PA-DREAD dimensions 1 to 5. D, R and E are formulas over the *Rubric* sheet; A is an analyst input read from the attack graph |
| Di strong, Di weak | Discoverability 1 to 5 in a strong and a weak geometric pass (analyst input read from the attack graph) |
| S strong, S weak | S = D + R + E + A + Di, 5 to 25 |
| Band strong, Band weak | Low (5 to 9), Medium (10 to 14), High (15 to 19), Critical (20 to 25) |
| First detection predicate / reason for Di; Affected-users basis | the reasons behind the two analyst inputs |
| Displacement route | for displacement threats, one of eight routes to the solver (Table 8 of the paper) |
| SATERA entries refined | the SC-1 to SC-17 entries of the earlier SATERA catalogue that this threat refines |
| SPARTA technique (confidence), ATT&CK technique (confidence), Mapping confidence | technique mappings; `high` (direct match), `medium` (needs a stated inference), `unmapped` |
| Review status | `Baseline: reproduces Table 5 of the paper` or `Validated: LLM panel and co-author evaluation` |
| Related CVEs (n), Related CVEs (IDs) | CVE records of the atlas related to the threat's assets (`—` if none) |
| Cross-layer propagation | layers and assets the effect can reach: `[A1.1]` the origin, `A1.3` an asset reached, `†` reached only through an inferred dependency (S1: A1.6 hosts A1.4 and A1.5; S2: A4.1 sets the policy of the PTP path A2.3); the last lines give the boundaries to the first check and to the ATM |

## Other catalogue sheets

* **Binding** (`threat_x_atlas_source_binding.csv`): Threat, Atlas #, Binding (`Attack` or `Path`), BibTeX key, source title, authors and year, source type, peer-reviewed (Yes/No),
  Level (E0 to E3) and Level (0 to 3), entry layer, impact layer, verified link (13 October 2026), mitigation IDs.
* **Assets** (`asset_register_27.csv`): ID, asset, layer, function, kind (hardware, software, service, data), STRIDE element type, trust boundary, component of the architecture figure,
  flags (external, timing, hosting), threats in the workbook and in the paper (check), CVEs mapped, cross-layer propagation of an attack on the asset.
* **Checks** (`paper_statistics_checks.csv`): Group, Statistic, Workbook (live formula), Paper (value stated in the paper), Check (OK), Paper location.
* **CVE Register** (`cve_register_57.csv`): the 57 CVE records mapped to assets and threats.
* **Rubric** (`rubric_raw.csv`): the lookup tables (evidence to base R, tier to E, goal to D with its rule, score to band).

## Atlas workbook, sheet *Threat Atlas* (`atlas_78_sources.csv`), one row per source

Columns 1 to 16 are the original review (title, authors and year, venue, venue ranking and its source, threat category, vulnerability category, attack category, exploitation
status, evidence basis, key findings, BibTeX key, domain, evidence level E0 to E3, placement in the paper draft); columns 17 to 24 are the atlas extension of 13 October 2026
(source type, peer-reviewed, citation, verified link and link check, normalised classes, one-line high-level attack); columns 25 to 40 add the asset, entry layer, impact layer,
direction (`Within layer`, `Upward (observables)`, `Downward (config / keys / sync)`), the boundaries crossed (TB1 to TB3), timing dependency, related CVEs, mitigation IDs, propagation notes,
atlas set, SATERA asset IDs and cross-layer propagation. A source *crosses a layer* when its direction is not `Within layer` (53 of 78).

## Panel files

See [../llm_panel/README.md](../llm_panel/README.md). The columns of `llm_panel/results/panel_long.csv` are: model, id, validity, layer, asset_ids_txt, stride_primary, stride_secondary_txt,
goal_Displacement, goal_Denial, goal_Deception, goal_Disclosure, is_enabler, adversary_class_txt, tier, evidence, analogue_only, D, R, E, A, Di_strong, Di_weak, S_strong, band_strong, S_weak,
band_weak, confidence (1 to 5, the model's own), issue, rationale, n_runs. `panel_summary.csv` has one row per threat with, for every field, the panel value, the catalogue value, the share of
models agreeing, and the tag `agree`, `panel_vs_catalogue` or `split`.
