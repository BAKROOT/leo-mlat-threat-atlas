# Limitations and notes

Read this before relying on the data.

## About the catalogue

* **Validation.** All 55 records were validated by a blind four-model LLM panel and then evaluated by the co-authors; the scores and algorithms were verified (`make check`). The *Review status* column separates 7 *Baseline* records (they reproduce Table 5 of the paper) from 48 *Validated* records. Validation is not field testing: see the next point.
* **Scores are ordinal.** They rank threats; they are not probabilities and not rater consensus. Bands are specific to this study.
* **No field validation yet.** Reconstruction of published attacks as chains, coverage against technique catalogues and independent expert review are future work. Much of the evidence is from analogue systems, and none was obtained on an orbital multilateration network.
* **Published design only.** The analysis concerns the SATERA reference design as published, not a fielded system. The detection level of the integrity monitor is not published, which is why the strong/weak assumptions W2 and W3 are hypotheses.
* **Two dependencies are inferred** (S1: A1.6 hosts A1.4 and A1.5; S2: A4.1 sets the policy of the PTP path A2.3). Assets reached only through them carry a dagger in the propagation lists.

## About what is released

* **Dependency-graph edge list not included.** The 41 edges (15 data, 5 timing, 7 control, 14 hosting) are described in the paper but are not a file in this release, so the radius, fan-in and Spearman statistics of Section 6 cannot be reproduced here.
  `scripts/asset_reach.py` reproduces what can be read from the reach lists of the *Assets* sheet.
* **Atlas text columns** are the authors' summaries of third-party work; follow the verified links to the sources. Links were verified on 13 October 2026.

## About the language-model panel

* **Models are not domain experts.** The models share training material, their errors may be correlated, and agreement is not correctness.
* **Uncontrolled settings.** The web applications fix neither the sampling settings nor the exact model build; each model answered each prompt once (apart from one repeat); the closed-book condition rests on the instruction in the prompt.
* **Small sample.** 55 items and 4 raters give wide intervals. The validity verdict has a low alpha (0.32) because almost all verdicts are `valid` (212 of 220): that is a prevalence effect, not disagreement.
* **Rubric shared with the catalogue.** The prompts carry the same rubric as the catalogue, so agreement partly measures how clear the rubric is.
* **Vendor effects.** Models can favour output of their own family (Panickssery et al., 2024). The analysis is therefore repeated without Claude and with each model left out in turn; no single model carries the results (see `docs/RESULTS.md`).
* **No external human raters.** The human evaluation was done by the co-authors; an independent study with external human raters has not been run.
* **Completeness mapping is single-coded** and has not been checked by a second coder. The models saw the architecture and the rubric, so their lists are not fully unprompted.
* **Replaced run.** The first ChatGPT run (14 small prompt parts, because the full B1 prompt was blocked) was replaced on 29 October 2026 by the full prompts so that all models saw the same text. The earlier run is kept in `llm_panel/sensitivity/chatgpt_small_parts/`; replacing it moved single values of alpha by at most 0.16.
* **Records not kept.** For ChatGPT's first session the exact thinking mode and date, and for the Gemini Flash-Lite run the exact date, were not recorded.
* **Prompt A wording.** Rules 2 and 3 of Prompt A mention "the authors' text" and `unknown_sources`, which do not exist in Prompt A. Harmless; left unchanged because the prompts had already been used.
