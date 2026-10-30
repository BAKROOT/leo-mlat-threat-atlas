# Panel protocol

How the language-model review was designed, run and analysed. Paper section: 4.11. Companion: [PROVENANCE.md](PROVENANCE.md) records what was actually done with which model.

## 1. Purpose and position

The catalogue and its scores are the authors' own derivation. The panel is the first stage of validation, followed by the co-authors' evaluation, with three jobs:

1. **Reproducibility**: can the classification and the scores be reproduced by readers who did not write them?
2. **Disagreement**: on which records and fields do readers disagree with each other or with the catalogue?
3. **Completeness**: which threats do models expect before they see any threat of the catalogue?

It is **not expert validation**. The models share much of their training material, none is accountable for its answers, and agreement shows that a derivation can be reproduced, not that it is right.
The catalogue was not changed in response to the panel, so the version reviewed is the version reported.

## 2. Material

* Catalogue: 55 threats (`data/catalogue`). The answer key is the catalogue workbook itself; it was never shown to a model.
* **Prompt A** (`prompts/A_elicitation.txt`, about 3,000 tokens): purpose and scope, system description, layers, 27-asset register, trust boundaries, transfer channels, assumptions W1 to W4,
  STRIDE-tau, goal, adversary-class, tier and evidence definitions, the PA-DREAD rubric and the JSON schema. **No threat is shown.** The model lists the threats it expects.
* **Prompts B1 to B4** (`prompts/B1_L1.txt` ... `B4_L4.txt`, about 5,000 to 7,500 tokens): the same blocks plus the threat cards of one layer (16, 12, 12, 15). Each card has the
  mechanism, the attack vector, the assets and the cited atlas sources. The category, goals, adversary class, tier, evidence level, reach, scores, bands and enabler flags are withheld, and the
  cards were scrubbed of hints (adversary-class codes, the words *enabler*, *tau* and *precondition*).
* Every prompt opens with a defensive-purpose statement and asks for classification and rating only: no attack parameters, procedures, code or tooling.
* `tools/make_prompts_round1.py` regenerates all prompts byte for byte from the catalogue workbook; `prompts/SHA256SUMS.txt` lists their hashes.

## 3. Conditions for every model

1. One **fresh chat per prompt** (five chats per model). Prompt A first and in its own chat.
2. Memory and history off (temporary or incognito chat, personalisation off).
3. **Closed book**: the prompt instructs the model not to browse, run code or use tools; tools and attachments were not used.
4. The **whole prompt as one message**, unedited, identical for every model (hash-checked).
5. The reply saved unedited (`responses_raw/`); the strict-JSON copy (`responses/`) differs only by removed code fences, curly quotes, comments and trailing commas, never by a value.
6. Model version, thinking mode, date and settings noted per run (`run_log.csv`). The model's own `meta.model_self_report` is **not** reliable (see PROVENANCE) and is not used.

## 4. Reply format (per rating prompt)

One JSON object: `meta`, `ratings` (one object per card) and `batch_comments` (`missing_threats`, at most five, and `rubric_ambiguities`). Each rating has:
`id`, `validity` (`valid | duplicate | not_a_threat | out_of_scope`), `related_id`, `layer`, `asset_ids`, `trust_boundary`, `stride_primary`, `stride_secondary`, `goals`, `is_enabler`,
`adversary_class`, `tier`, `evidence`, `analogue_only`, `unknown_sources` (cited sources the model could not assess), `D`, `R`, `E`, `A`, `Di_strong`, `Di_weak` (1 to 5; null for enablers' D),
`confidence` (1 guess to 5 certain), `rationale` (at most 45 words) and `issue` (at most 30 words). Prompt A returns `threats` (title, layer, assets, STRIDE-tau, goals, tier, evidence support, severity,
whether commonly overlooked), `architecture_weaknesses` and `overall`.

## 5. Validation and merge (`tools/validate_merge.py`)

Checks every file against the schema (vocabulary, ranges, every expected id exactly once), writes a repair prompt for each failing file, and merges everything. Warnings are consistency notes, not failures
(for example R not matching the model's own evidence level, E not matching its tier, goals given for an enabler). **Result: 220 of 220 ratings valid, 0 repairs.** The merge gives one row per model and threat
(`results/panel_long.csv`); where a threat was rated in several runs the values are collapsed by the median.

## 6. Statistics

* **Krippendorff's alpha** (`tools/agreement.py`): nominal for categories and goal flags, ordinal for tier and evidence level, interval for scores; missing ratings (enablers have no D) are handled;
  95% percentile bootstrap over threats (1000 resamples, seed 7). Limits: 0.800 and above reliable, 0.667 to 0.800 tentative, below not reliable (Krippendorff).
* **Kendall's W** on the rankings of the threats, with tie correction, for the scores; it ignores differences in level, which alpha counts as disagreement.
* Three rater sets: the four models; the three without Claude (a vendor-effect check, because models tend to favour output of their own family); the four models plus the catalogue as a fifth rater. Leave-one-out for every model.
* **Model against catalogue**: exact match for categories, within one point for scores, mean absolute error, goal-set Jaccard, Spearman's rho of S, band match, overlap of the top 10.
* **Consensus tags** per threat and field: `agree` (at least 2/3 of the models, or an interquartile range of at most 1 for a score, and the catalogue agree), `panel_vs_catalogue` (the models agree with each other, not with the catalogue),
  `split` (no consensus). **Contested threats**: band differs between models with a spread of S of 4 or more, or a rank spread of one half or more, or an impact spread of 4 or more, or a likelihood spread of 5 or more.
* **Test-retest** (`tools/retest.py`): one prompt twice in two fresh chats.
* **Completeness**: each of the 143 threats listed in Prompt A is mapped to a catalogue threat as *C* (matches), *P* (related: narrower or different) or *N* (no counterpart). This mapping is a human-style judgement, made by one analyst;
  `Elicit_coverage_heur` in `results/Panel_Review.xlsx` is a word-and-asset-overlap heuristic that only suggests candidates.

## 7. Repeat it

See `llm_panel/README.md`, section *Repeat the review with another model*.
