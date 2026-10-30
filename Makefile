# One-command checks. Run from the repository root.
PY ?= python

.PHONY: check panel sensitivity figures export tables test all clean

check:            ## recompute the paper's counts and every PA-DREAD score from the workbooks
	$(PY) scripts/check_paper_counts.py
	$(PY) scripts/asset_reach.py

panel:            ## re-run the panel analysis from the stored responses and compare with llm_panel/results/
	cd llm_panel && $(PY) tools/validate_merge.py --out results_rebuilt > /dev/null
	cd llm_panel && $(PY) tools/agreement.py --long results_rebuilt/panel_long.csv --out results_rebuilt > /dev/null
	cd llm_panel && $(PY) tools/retest.py responses/chatgpt__B3__run1.json retest/responses/chatgpt__B3__run2.json --out results_rebuilt/retest_chatgpt_B3_run1_vs_run2.csv > /dev/null
	@for f in panel_long.csv panel_summary.csv disagreements.csv model_vs_catalogue.csv agreement_alpha.csv agreement_alpha_vs_W.csv retest_chatgpt_B3_run1_vs_run2.csv; do \
	  cmp -s llm_panel/results_rebuilt/$$f llm_panel/results/$$f && echo "identical: $$f" || { echo "DIFFERENT: $$f"; exit 1; }; done
	@echo "panel analysis reproduces llm_panel/results/"

sensitivity:      ## re-run the analysis with ChatGPT's first-session small parts in the ChatGPT seat
	rm -rf llm_panel/results_sens && mkdir -p llm_panel/results_sens/responses
	cp llm_panel/responses/*.json llm_panel/results_sens/responses/
	rm llm_panel/results_sens/responses/chatgpt__B[1-4]__run1.json
	cp llm_panel/sensitivity/chatgpt_small_parts/responses/*.json llm_panel/results_sens/responses/
	rm llm_panel/results_sens/responses/chatgpt__B1a__run3.json llm_panel/results_sens/responses/chatgpt__B1a__run4.json
	cd llm_panel && $(PY) tools/validate_merge.py --responses results_sens/responses --out results_sens/out > /dev/null
	cd llm_panel && $(PY) tools/agreement.py --long results_sens/out/panel_long.csv --out results_sens/out > /dev/null
	@for f in panel_long.csv panel_summary.csv disagreements.csv model_vs_catalogue.csv agreement_alpha.csv; do \
	  cmp -s llm_panel/results_sens/out/$$f llm_panel/sensitivity/chatgpt_small_parts/results/$$f && echo "identical: $$f" || { echo "DIFFERENT: $$f"; exit 1; }; done

figures:          ## redraw the four panel figures
	cd llm_panel/figures && $(PY) fig_agree.py > /dev/null && $(PY) fig2.py > /dev/null && $(PY) fig3.py > /dev/null && $(PY) fig4.py > /dev/null && $(PY) fig1.py > /dev/null
	@echo "figures written to llm_panel/figures/out/"

export:           ## refresh the CSV snapshots of the workbooks
	$(PY) scripts/export_csv.py

tables:           ## regenerate docs/RESULTS_TABLES.md
	$(PY) scripts/make_results_tables.py

test:             ## everything under pytest
	$(PY) -m pytest -q

all: check panel figures test

clean:
	rm -rf llm_panel/results_rebuilt llm_panel/results_sens .pytest_cache
