# Figures

* The four figures of the panel section (protocol, agreement, disagreement, completeness) are drawn by `llm_panel/figures/*.py`; PDF and PNG output is in `llm_panel/figures/out/`
  and PNG copies are in `docs/images/` for the documentation. `make figures` redraws them.
* `paper/Fig6_A1.5_end_to_end_threat_modelling.pdf` and `.png`: the end-to-end worked example of the paper on one asset (the onboard clock subsystem A1.5), from decomposition to score.
* The other figures of the paper (architecture, layered asset diagram, trust boundaries, attack graphs, reach charts) are TikZ and pgfplots sources inside the manuscript and are published with it.
