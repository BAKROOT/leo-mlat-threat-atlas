# Independent expert validation: protocol and materials

Status: **not yet performed.** This folder holds the materials so that the study can be run without changing the catalogue. The panel of language models in `llm_panel/` is supplementary and tests reproducibility only; it says nothing about validity.

## Design

* Raters: at least two independent experts in each of satellite security, GNSS and timing, ADS-B and multilateration, and cyber-physical security (8 or more in all). None took part in the derivation.
* Sample: 20 threats, stratified at random by `sample_threats.py` (seed 20261112): at least four per layer, and every STRIDE-tau primary category, every evidence level and every adversary class at least once. The sample is fixed and published before any rating is collected (`sample.csv`).
* Material: the same blind prompt cards as the models (`llm_panel/prompts/`) and the same rubric (sheet *Rubric*), one card per threat and rater, without discussion between raters and without access to the catalogue's own values.
* Fields rated (`rating_form_template.csv`): STRIDE-tau primary and secondary, evidence level, adversary class, tier, the PA-DREAD dimensions D, R, E, A and Di (strong and weak pass), and a 1 to 5 confidence.
* The catalogue is **not changed** before the ratings are collected.

## Analysis

* Krippendorff's alpha, nominal for STRIDE-tau, evidence level and adversary class, ordinal for tier and the PA-DREAD dimensions, with 95 % bootstrap intervals over threats (`krippendorff_alpha.py`, verified against the `krippendorff` package on random data).
* Reported between the experts and between the experts and the catalogue, against limits fixed in advance: 0.800 reliable, 0.667 to 0.799 tentative, below 0.667 not reliable.
* Disagreements are reported by field and threat; any change to the catalogue is a new release with a change-log entry.

## Run

```
python validation/sample_threats.py                       # writes validation/sample.csv
python validation/krippendorff_alpha.py ratings_long.csv nominal 2000 1
python validation/krippendorff_alpha.py ratings_long.csv ordinal 2000 1
```

`ratings_long.csv` has the columns `unit,rater,value`: one file per field, one row per threat and rater, empty values for missing ratings.

## Expert instructions (short)

Read the threat card and rate each field from the rubric alone. Where the card does not allow a rating, leave the field empty and say why in the comment. Do not look up the catalogue or the paper, and do not discuss the cards with the other raters before submitting.
