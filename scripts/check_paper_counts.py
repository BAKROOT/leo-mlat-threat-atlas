#!/usr/bin/env python3
"""
Recompute, from the two workbooks and without using their Excel formulas, the figures that the paper states
about the catalogue and the atlas, and re-derive every PA-DREAD score from the rubric.

Usage (from the repository root):   python scripts/check_paper_counts.py
Exit code 0 when every check passes, 1 otherwise.  Requires pandas, openpyxl.

Three groups of checks
  A. Counts stated in the paper (size of the catalogue, threats per layer, STRIDE-tau categories, postulated
     threats, bands, size of the atlas, share of sources that cross a layer).
  B. Scores: R from the evidence level (minus one level when the evidence is from an analogue system only),
     E from the adversary tier, D from the goals and the affected users, S = D+R+E+A+Di and the band from S,
     recomputed for every threat and compared with the value stored in the workbook.
  C. The workbook's own 'Checks' sheet (112 statistic-by-statistic comparisons): all must read OK.
"""
import os, sys
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "data/catalogue/SATERA_Extended_Threat_Catalogue.xlsx")
ATL = os.path.join(ROOT, "data/atlas/PRISM-LEO_Threat_Exploit_Atlas.xlsx")

R_BASE = {"P": 1, "E0": 2, "E1": 3, "E2": 4, "E3": 5}                  # Rubric sheet, evidence -> base R
E_OF_TIER = {"T1p": 5, "T1c": 4, "T2": 3, "T3": 2, "T3x": 1}            # Rubric sheet, tier -> E
def band(s): return "Critical" if s >= 20 else "High" if s >= 15 else "Medium" if s >= 10 else "Low"

results = []
def check(group, name, got, want):
    ok = got == want
    results.append((ok, group, name, got, want))

def main():
    cat = pd.read_excel(CAT, sheet_name="Catalogue", header=3)
    cat = cat[cat["ID"].astype(str).str.match(r"T\d\.\d+$")].copy()
    atl = pd.read_excel(ATL, sheet_name="Threat Atlas", header=4)
    atl = atl[pd.to_numeric(atl["#"], errors="coerce").notna()].copy()

    # ---- A. counts stated in the paper
    check("A", "threats in the catalogue", len(cat), 55)
    for layer, n in zip(["L1", "L2", "L3", "L4"], [16, 12, 12, 15]):
        check("A", f"threats at {layer}", int((cat["Layer"] == layer).sum()), n)
    stride = cat["STRIDE-tau primary"].value_counts().to_dict()
    for k, n in {"T": 19, "D": 12, "E": 8, "S": 7, "I": 5, "R": 2, "tau": 2}.items():
        check("A", f"primary STRIDE-tau category {k}", int(stride.get(k, 0)), n)
    check("A", "postulated threats (no published evidence)", int((cat["Evidence"] == "P").sum()), 16)
    check("A", "enablers", int((cat["Role"] == "Enabler").sum()), 4)
    check("A", "High or Critical, strong pass", int(cat["Band strong"].isin(["High", "Critical"]).sum()), 47)
    check("A", "High or Critical, weak pass", int(cat["Band weak"].isin(["High", "Critical"]).sum()), 47)
    check("A", "atlas sources", len(atl), 78)
    crossing = int((atl["Direction (derived)"] != "Within layer").sum())
    check("A", "atlas sources that cross a layer", crossing, 53)
    check("A", "share of atlas sources that cross a layer (%)", round(100 * crossing / len(atl)), 68)
    cve = pd.read_excel(ATL, sheet_name="CVE Register", header=4)
    check("A", "CVE records", int(pd.to_numeric(cve["#"], errors="coerce").notna().sum()), 57)
    mit = pd.read_excel(ATL, sheet_name="Mitigations", header=4)
    check("A", "mitigations", int(mit["ID"].astype(str).str.match(r"M\d+$").sum()), 25)

    # ---- B. scores re-derived from the rubric
    leaf = cat[cat["Role"] != "Enabler"]
    for _, r in cat.iterrows():
        tid = r["ID"]
        base = R_BASE[r["Evidence"]]
        R = max(1, base - 1) if str(r["Analogue only"]).strip().upper().startswith("Y") and r["Evidence"] != "P" else base
        check("B", f"{tid} R from evidence", int(r["R"]), R)
        check("B", f"{tid} E from tier", int(r["E"]), E_OF_TIER[r["Tier code"]])
    for _, r in leaf.iterrows():
        tid = r["ID"]
        goals = {g for g in ["Displacement", "Denial", "Deception", "Disclosure"] if str(r[g]).strip().upper().startswith("Y")}
        if "Displacement" in goals: D = 5
        elif "Deception" in goals: D = 4
        elif "Denial" in goals: D = 3 if r["A"] >= 3 else 2
        else: D = 1
        check("B", f"{tid} D from goals", int(r["D"]), D)
        for tag, di, s, b in [("strong", "Di strong", "S strong", "Band strong"), ("weak", "Di weak", "S weak", "Band weak")]:
            S = int(r["D"] + r["R"] + r["E"] + r["A"] + r[di])
            check("B", f"{tid} S {tag} = D+R+E+A+Di", int(r[s]), S)
            check("B", f"{tid} band {tag}", r[b], band(S))

    # ---- C. the workbook's own Checks sheet
    chk = pd.read_excel(CAT, sheet_name="Checks", header=3)
    chk = chk[chk["Check"].isin(["OK", "CHECK", "FAIL", "DIFF"]) | chk["Check"].astype(str).str.upper().isin(["OK"])]
    check("C", "rows of the workbook's Checks sheet", len(chk), 112)
    check("C", "rows of the Checks sheet that read OK", int((chk["Check"] == "OK").sum()), 112)

    bad = [r for r in results if not r[0]]
    for g in "ABC":
        sub = [r for r in results if r[1] == g]
        print(f"group {g}: {sum(r[0] for r in sub)} of {len(sub)} checks pass")
    for ok, g, name, got, want in bad:
        print(f"  FAIL [{g}] {name}: workbook/recomputed = {got!r}, expected = {want!r}")
    print("ALL CHECKS PASS" if not bad else f"{len(bad)} CHECK(S) FAIL")
    return 0 if not bad else 1

if __name__ == "__main__":
    sys.exit(main())
