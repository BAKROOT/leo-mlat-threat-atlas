# Contributing

Corrections and extensions are welcome, especially:

* **Errors** in a catalogue record, a binding to an atlas source, a link or a count: open an issue with the record ID (for example T3.07 or atlas #42) and the evidence.
* **New atlas sources**: add a row under a new number (#79 onwards); never renumber existing sources. Give the evidence level (E0 to E3), the layer entered and affected, a verified link and the
  mechanism at a high level. No parameters, procedures or tooling (see `docs/RESPONSIBLE_USE.md`).
* **More reviewers**: run the panel protocol with another model or with human raters (`llm_panel/README.md`) and send the response files and the run log entry.
* **A second coder** for `llm_panel/completeness/elicitation_mapping_manual.csv`.

Before sending a change run `make test`. Changes to the workbooks should keep the *Checks* sheet at OK and `make check` passing; regenerate the CSV snapshots with `make export`.
