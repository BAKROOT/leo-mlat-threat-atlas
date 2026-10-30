# Provenance

What was run, with which models, when, under which settings, and what deviated from the protocol. The per-run record is `llm_panel/run_log.csv`; the command-by-command log is `llm_panel/COMMANDS_LOG.txt`.

## Main panel

| Seat | Model as used | Mode | Date | Files | Notes |
|---|---|---|---|---|---|
| Claude | Claude Sonnet 5.5 (claude.ai) | High | 25 Oct 2026 | `claude__A,B1-B4__run1.json` | incognito chat; a fresh chat per prompt |
| ChatGPT | GPT-6 (web app) | Think (composer mode) | 29 Oct 2026 for B1 to B4; Prompt A from an earlier session (date and mode not recorded) | `chatgpt__A,B1-B4__run1.json` | temporary chat, personalisation off, no tools, no attachments; prompt hash checked in the composer before sending; reply hash verified after copying |
| DeepSeek | DeepSeek web app | DeepThink on | 25 Oct 2026 | `deepseek__A,B1-B4__run1.json` | web search off; the model's own `meta.model_self_report` says OpenAI/GPT-4.1 for B1 to B4; the operator confirmed the app was DeepSeek; self-reports are unreliable and not used |
| Gemini | Gemini 3.1 Pro (Edu account) | default | 25 Oct 2026 | `gemini__A,B1-B4__run2.json` | a new chat per prompt; the self-report string (2.5 Flash, GPT-4, 2.5 Pro) is unreliable |

Every model received byte-identical prompts (`prompts/`, hashes in `prompts/SHA256SUMS.txt`). One run per model and prompt; no repair prompts were needed.

## Runs kept apart

| What | Where | Why not in the main panel |
|---|---|---|
| ChatGPT, first session: 14 small prompt parts (B1a to B4d) and four B1a runs | `llm_panel/sensitivity/chatgpt_small_parts/` | the full B1 prompt was blocked in that session, so the prompts differed from the other models; replaced on 29 Oct 2026 by the full prompts |
| Gemini Flash-Lite (signed out), run1 | `llm_panel/sensitivity/gemini_flash_lite/` | thin output; Gemini 3.1 Pro (run2) replaced it |
| ChatGPT B3 run2 | `llm_panel/retest/` | test-retest of B3 run1; identical prompt in a new temporary chat |

For the small-part session, B1a run1 and run2 differ in whether the attack-vector line was present, and which is which was not recorded; run3 (with) and run4 (without) of 29 Oct 2026 are fully recorded.

## Integrity of the record

* Replies are stored twice: as copied (`responses_raw/`) and as strict JSON (`responses/`), where only code fences, curly quotes, comments and trailing commas were removed.
* For the ChatGPT runs of 29 Oct 2026 each prompt's SHA-256 was computed from the composer text and compared with the file before sending, and each reply's SHA-256 was compared with the saved file. In two runs (B3, B4) the browser link dropped after sending and the reply was read afterwards from the same chat, unchanged.
* The analysis reproduces from the stored files: `make panel` rebuilds `llm_panel/results/` exactly (220 ratings, 0 differences); `tools/make_prompts_round1.py` rebuilds all prompts byte for byte.
* The shared blocks (purpose, system description, layers, asset register, trust boundaries, channels, assumptions, definitions, rubric) are word for word identical in every prompt file. Threat ids and counts in every B prompt match `manifest.json`.
  No catalogue category, goal, tier, evidence level, reach, score or band appears in a card.

## Validation of the catalogue

1. **LLM panel (blind).** Four models from four vendors rated all 55 threats without seeing the catalogue's own classification or scores, and listed threats from the architecture alone (the runs above).
2. **Evaluation by the co-authors.** The co-authors evaluated the panel's agreements and disagreements with the catalogue and finalised it.
3. **Verification of scores and algorithms.** `make check` recomputes every count the paper states and every PA-DREAD score (388 checks); `make panel` recomputes the panel statistics from the stored replies.

The mapping of the 143 listed threats to the catalogue (completeness) is single-coded and has not been checked by a second coder. The panel statistics are reported for the four models and for the model sets with one model left out, so that no single vendor drives a result.

## Dates

Catalogue built 20 Oct 2026 and extended with CVE and propagation columns on 29 Oct 2026; final release v1.3 of the catalogue and the atlas 30 Oct 2026; panel runs 25 and 29 Oct 2026; analysis, figures and this repository 30 Oct 2026. Links in the atlas were verified on 13 Oct 2026.
