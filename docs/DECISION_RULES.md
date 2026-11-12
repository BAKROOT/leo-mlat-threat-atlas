# Decision rules of the framework (manuscript supplementary material, version 2.0)

## PA-DREAD is a modified ranking, not DREAD

It keeps the five names and the 1 to 5 ordinal scale and changes two meanings: Reproducibility is evidence strength (the best evidence among the bound atlas entries, one lower if analogue only) and Discoverability is detection depth (the first layer whose check flags the effect, 5 if none does). Every dimension is anchored on a named artefact, and the strong and the weak geometric pass are scored separately. Totals rank threats within this study; they are not comparable with conventional DREAD totals or with the scores of another study. Bands: Low 5-9, Medium 10-14, High 15-19, Critical 20-25 (the last holds six integer totals). The rubric and worked examples are in the workbook sheets *Rubric* and *Worked*.

## STRIDE-tau decision rules

The primary category is the violation that the *primary effect on the asset* causes; every other violation is secondary. Rules are applied in this order.

| Category | Rule (primary effect) | Defeated by | Examples |
|---|---|---|---|
| Spoofing (S) | A party, emitter or source is taken for another: a forged message or emission is accepted as genuine. A replayed genuine message accepted as current is Spoofing, Tampering secondary | Source authentication; freshness for a replay | T1.01, T1.02, T2.02, T2.07 |
| Tampering (T) | Content, state or configuration is altered, whoever alters it. A message that arrives intact but late is not Tampering | Message authentication and integrity protection; change control | T2.01, T3.04, T4.01 |
| Delay on a data asset | A message or report is held back or reordered on an asset that is not on the timing dependency: Tampering when content or order changes, Denial of Service when the effect is loss. A delay that moves no clock is not tau | Freshness and sequence checks; time-outs | T2.03 |
| Temporal integrity (tau) | An offset, drift or delay appears in the time reference of an asset on the timing dependency (A1.2, A1.5, A2.3, A3.2, A4.1) **and survives the test**: with every message authentic, fresh and source-authenticated the offset is still achieved | Integrity of the time of arrival; clock synchronisation and cross-checking against an independent time source; not message authentication | T1.11, T2.06 |
| Spoofing with tau secondary | The offset is achieved only by a forged message: authentication removes it | Source or message authentication | T2.07 |

## Authentication-invariance test

1. Assume every message and command on the path carries sound message and source authentication and a freshness proof (assumption A3).
2. Ask whether a time offset on an asset of the timing dependency is still achieved.
3. If yes, the primary category is tau; the applicable checks are the integrity of the time of arrival and clock synchronisation, because neither involves a message.
4. If no, the threat takes the conventional category its primary effect violates, and a remaining time offset is recorded as a secondary tau effect.

The test is applied only to threats on or reaching the five timing assets; for all others the catalogue column reads "n/a".

## PASTA traceability

| Stage | Input | Output artefact | Used by |
|---|---|---|---|
| 1 Objectives | Surveillance requirements, Part-IS and ED-205A obligations | Security properties per asset; four L4 goals (displacement, denial, deception, disclosure) | Damage (D); chains |
| 2 Scope | SATERA design papers | Scope, assumptions A1-A4, architecture | Stage 3 |
| 3 Decomposition | Stages 1-2 | 27 assets, boundaries TB0-TB3, five timing assets, flows; asset register | Catalogue asset column; graph nodes; Affected users (A) |
| 4 Threat analysis | Stage 3, adversary classes AC1-AC7 and tiers T1-T3 | STRIDE-tau catalogue of 55 threats | Exploitability (E); chains |
| 5 Vulnerability analysis | Atlas of 78 sources, CVE register, mitigations | Evidence level per threat; CVE and mitigation bindings | Reproducibility (R) |
| 6 Attack modelling | Stages 3-5 | Effect-transfer graphs, the dependency graph, the stealth window | Discoverability (Di); reach; chains |
| 7 Risk and impact | Stages 1-6 | PA-DREAD scores and bands, strong and weak pass | Ranking; findings |

## Graph semantics

A node is an asset. A directed edge a -> b means a compromise or fault at a can change the input, state or behaviour of b: a relation of causal reachability with no probability, no AND/OR and no cost. Data and timing edges are flow edges; control and hosting edges are authority edges. **Reachability is not exploitability**: a threat can use a path only if the adversary has the access of its class and tier at the entry asset, the effect survives the checks on the path, and the preconditions of the threat hold (`data/derived/preconditions.csv`).
