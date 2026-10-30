# Licence for data, prompts, responses, figures and documentation

Unless a file says otherwise, everything in this repository that is not source code is released under the
**Creative Commons Attribution 4.0 International licence (CC BY 4.0)**:
<https://creativecommons.org/licenses/by/4.0/legalcode>.

This covers the workbooks and CSV files in `data/`, the prompts, responses, results and figures in `llm_panel/`
and `figures/`, and the documents in `docs/`. You may share and adapt them for any purpose, including commercially,
if you give appropriate credit (cite the paper and this repository, see `CITATION.cff`), link to the licence and
indicate whether you made changes.

Source code (`*.py`, `Makefile`, `tests/`) is released under the MIT licence in `LICENSE`.

## What the licence does not cover

* **Third-party works named in the atlas.** The atlas lists titles, authors, venues and links of published papers, CVE
  identifiers, and technique identifiers of MITRE ATT&CK and SPARTA. These identifiers and the cited works belong to their
  owners and are used here to give references, not republished.
* **Model replies.** The files in `llm_panel/responses/` and `responses_raw/` are the unedited output of third-party
  language-model services, produced in response to the prompts of this study. They are released for scientific reproducibility;
  check the terms of the respective service if you wish to use them for other purposes, for example to train a model.

## Authorship

The catalogue, the evidence atlas, the analysis scripts and the figure scripts are the work of the authors named in `CITATION.cff`.
How the catalogue was validated is described in `docs/PROVENANCE.md`.
