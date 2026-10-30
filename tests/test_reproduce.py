"""
Reproduction tests. Run from the repository root:  python -m pytest -q
Each test recomputes something from the stored inputs and compares it with the stored result.
"""
import filecmp, hashlib, json, os, subprocess, sys
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "llm_panel")
CAT = os.path.join(ROOT, "data/catalogue/SATERA_Extended_Threat_Catalogue.xlsx")

def run(args, cwd=ROOT):
    return subprocess.run([sys.executable] + args, cwd=cwd, capture_output=True, text=True)

def test_paper_counts_and_scores():
    r = run(["scripts/check_paper_counts.py"])
    assert r.returncode == 0, r.stdout[-2000:]
    assert "ALL CHECKS PASS" in r.stdout

def test_asset_reach_statement():
    r = run(["scripts/asset_reach.py"])
    assert r.returncode == 0, r.stdout[-1500:]
    assert len(pd.read_csv(os.path.join(ROOT, "data/derived/asset_reach.csv"))) == 27

def test_csv_snapshots_have_expected_rows():
    cat = pd.read_csv(os.path.join(ROOT, "data/catalogue/csv/catalogue_55_threats.csv"))
    atl = pd.read_csv(os.path.join(ROOT, "data/atlas/csv/atlas_78_sources.csv"))
    assert len(cat) == 55 and len(atl) == 78
    assert len(pd.read_csv(os.path.join(ROOT, "data/catalogue/csv/cve_register_57.csv"))) == 57

def test_prompt_hashes():
    sums = os.path.join(PANEL, "prompts/SHA256SUMS.txt")
    for line in open(sums, encoding="utf-8"):
        digest, name = line.split()
        assert hashlib.sha256(open(os.path.join(PANEL, "prompts", name), "rb").read()).hexdigest() == digest, name

def test_prompts_regenerate_byte_for_byte(tmp_path):
    r = run(["tools/make_prompts_round1.py", CAT, str(tmp_path)], cwd=PANEL)
    assert r.returncode == 0, r.stderr[-1500:]
    for name in ["A_elicitation.txt", "B1_L1.txt", "B2_L2.txt", "B3_L3.txt", "B4_L4.txt", "manifest.json"]:
        assert filecmp.cmp(tmp_path / "prompts" / name, os.path.join(PANEL, "prompts", name), shallow=False), name
    small = os.path.join(PANEL, "sensitivity/chatgpt_small_parts")
    for sub, stored in [("small", "prompts"), ("small_nv", "prompts_no_attack_vector")]:
        for f in os.listdir(os.path.join(small, stored)):
            assert filecmp.cmp(tmp_path / "prompts" / sub / f, os.path.join(small, stored, f), shallow=False), f

def test_every_response_is_complete():
    manifest = json.load(open(os.path.join(PANEL, "prompts/manifest.json")))
    resp = os.path.join(PANEL, "responses")
    files = [f for f in os.listdir(resp) if f.endswith(".json")]
    assert len(files) == 20                        # 4 models x (A + B1..B4)
    n = 0
    for f in files:
        d = json.load(open(os.path.join(resp, f), encoding="utf-8"))
        prompt = f.split("__")[1]
        if prompt != "A":
            ids = [r["id"] for r in d["ratings"]]
            assert ids == manifest[prompt]["expected_ids"], f
            n += len(ids)
    assert n == 220

PANEL_OUTPUTS = ["panel_long.csv", "panel_summary.csv", "disagreements.csv", "model_vs_catalogue.csv",
                 "agreement_alpha.csv", "agreement_alpha_vs_W.csv", "retest_chatgpt_B3_run1_vs_run2.csv"]

def test_panel_analysis_reproduces(tmp_path):
    out = str(tmp_path / "out")
    assert run(["tools/validate_merge.py", "--out", out], cwd=PANEL).returncode == 0
    assert run(["tools/agreement.py", "--long", out + "/panel_long.csv", "--out", out], cwd=PANEL).returncode == 0
    assert run(["tools/retest.py", "responses/chatgpt__B3__run1.json", "retest/responses/chatgpt__B3__run2.json",
                "--out", out + "/retest_chatgpt_B3_run1_vs_run2.csv"], cwd=PANEL).returncode == 0
    for f in PANEL_OUTPUTS:
        assert filecmp.cmp(os.path.join(out, f), os.path.join(PANEL, "results", f), shallow=False), f

def test_headline_numbers():
    a = pd.read_csv(os.path.join(PANEL, "results/agreement_alpha.csv")).set_index("metric").value
    assert round(a["Krippendorff alpha (nominal): layer"], 2) == 0.95
    assert round(a["Krippendorff alpha (nominal): stride_primary"], 2) == 0.88
    assert round(a["Krippendorff alpha (interval): D"], 2) == 0.90
    assert round(a["Krippendorff alpha (interval): A"], 2) == 0.81
    L = pd.read_csv(os.path.join(PANEL, "results/panel_long.csv"))
    assert len(L) == 220 and L.validity.value_counts().to_dict()["valid"] == 212

def test_results_tables_are_current(tmp_path):
    out = str(tmp_path / "tables.md")
    assert run(["scripts/make_results_tables.py", out]).returncode == 0
    assert filecmp.cmp(out, os.path.join(ROOT, "docs/RESULTS_TABLES.md"), shallow=False)
