#!/usr/bin/env python3
"""
Cross-layer reach per asset, read from the 'Assets' sheet of the catalogue workbook.

For each of the 27 assets the sheet lists the layers and assets that an effect starting at that asset can reach
along the data, timing, control and hosting dependencies of the paper (assets reached only through the two inferred
dependencies S1 and S2 carry a dagger). This script parses those lists and writes data/derived/asset_reach.csv:
number of other assets reached, number of layers reached, number reached only through S1/S2, boundaries to the
first check and to the ATM, and the number of catalogue threats against the asset.

It then tests one statement of the paper (Section 5.5, finding F2): the operator and supplier asset A4.7, the
mission-operations asset A4.8 and the control assets reach 16 to 23 of the other 26 assets and have 2 to 4 threats
each. 'The control assets' is read here as A4.1, A4.3 and A4.4 (the L4 assets on the control path); the paper does not
list them by identifier.

It also reproduces, from the same lists, the fan-in of the processing assets (A3.3 21, A3.4 22, A3.5 22, A3.6 24) and the
Spearman rank correlation between radius and threat count (0.22, p = 0.26, 27 assets). The 40 edges recoverable from the
'Asset Connections' sheet give exactly these lists; the manuscript counts 40 edges; provenance and sensitivity are in graph/ and data/derived (see docs/LIMITATIONS.md).

Usage (from the repository root):   python scripts/asset_reach.py        Requires pandas, openpyxl.
"""
import os, re, sys
import pandas as pd
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "data/catalogue/LEO_MLAT_Threat_Catalogue.xlsx")

def main():
    df = pd.read_excel(CAT, sheet_name="Assets", header=3)
    df = df[df["ID"].astype(str).str.match(r"A\d\.\d+$")].copy()
    col = [c for c in df.columns if str(c).startswith("Cross-layer propagation")][0]
    out = []
    for _, r in df.iterrows():
        text = str(r[col])
        ids = set(re.findall(r"A\d\.\d+", text)) - {r["ID"]}
        daggered = set(re.findall(r"(A\d\.\d+)†", text)) - {r["ID"]}
        layers = len({i[1] for i in ids} | {r["ID"][1]})
        m1 = re.search(r"to first check A3\.4/A3\.5: (\d+)", text); m2 = re.search(r"to ATM A4\.6: (\d+)", text)
        out.append(dict(asset=r["ID"], name=r["Asset"], threats=int(r["Threats (workbook)"]), assets_reached=len(ids),
                        of_other_assets=len(df) - 1, layers_reached=layers, reached_only_via_inferred_S1_S2=len(daggered),
                        boundaries_to_first_check=int(m1.group(1)) if m1 else "", boundaries_to_ATM=int(m2.group(1)) if m2 else ""))
    res = pd.DataFrame(out)
    os.makedirs(os.path.join(ROOT, "data/derived"), exist_ok=True)
    res.to_csv(os.path.join(ROOT, "data/derived/asset_reach.csv"), index=False)
    print(res[["asset", "name", "threats", "assets_reached", "layers_reached"]].to_string(index=False))
    sel = res[res.asset.isin(["A4.1", "A4.3", "A4.4", "A4.7", "A4.8"])]
    ok = sel.assets_reached.between(16, 23).all() and sel.threats.between(2, 4).all() and len(res) == 27
    print("\nF2 (A4.1, A4.3, A4.4, A4.7, A4.8 reach 16 to 23 of the other 26 assets with 2 to 4 threats each):",
          "PASS" if ok else "FAIL")
    sets = {r["ID"]: set(re.findall(r"A\d\.\d+", str(r[col]))) - {r["ID"]} for _, r in df.iterrows()}
    fan = {a: sum(a in v for v in sets.values()) for a in sets}
    rho, p = spearmanr(res.assets_reached, res.threats)
    print("fan-in A3.3/A3.4/A3.5/A3.6:", fan["A3.3"], fan["A3.4"], fan["A3.5"], fan["A3.6"])
    print(f"Spearman radius vs threat count: {rho:.2f} (p = {p:.2f})")
    ok = ok and [fan[a] for a in ("A3.3", "A3.4", "A3.5", "A3.6")] == [21, 22, 22, 24] and round(rho, 2) == 0.22
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
