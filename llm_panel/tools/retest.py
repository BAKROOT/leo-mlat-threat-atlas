#!/usr/bin/env python3
"""
Test-retest of one model on one prompt: the same prompt sent twice in two fresh chats.

Usage (from llm_panel/):
    python tools/retest.py responses/chatgpt__B3__run1.json retest/responses/chatgpt__B3__run2.json \
        --out results/retest_chatgpt_B3_run1_vs_run2.csv

For every score (D, R, E, A, Di_strong, Di_weak, S_strong, S_weak) it gives the number of threats rated in
both runs, the share of identical scores, the share within one point, the mean absolute difference,
Krippendorff's alpha (interval, two raters) and Spearman's rho. For the categorical fields (validity, STRIDE-tau primary, tier, evidence, enabler flag) only the share
of identical values is given. Requires numpy, pandas, scipy.
"""
import argparse, importlib.util, json, os
import numpy as np, pandas as pd
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("agreement", os.path.join(HERE, "agreement.py"))
ag = importlib.util.module_from_spec(spec); spec.loader.exec_module(ag)

def load(path):
    with open(path, encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)["ratings"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run1"); ap.add_argument("run2"); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    r1, r2 = load(a.run1), load(a.run2)
    ids = [i for i in r1 if i in r2]
    rows = []
    for k in ["D", "R", "E", "A", "Di_strong", "Di_weak", "S_strong", "S_weak"]:
        pairs = []
        for i in ids:
            if k in ("S_strong", "S_weak"):
                dims = ["D", "R", "E", "A", "Di_strong" if k == "S_strong" else "Di_weak"]
                v1 = [r1[i].get(d) for d in dims]; v2 = [r2[i].get(d) for d in dims]
                if None in v1 or None in v2: continue
                pairs.append((sum(v1), sum(v2)))
            else:
                x, y = r1[i].get(k), r2[i].get(k)
                if x is None or y is None: continue
                pairs.append((x, y))
        p = np.array(pairs, float)
        if len(p) < 2: continue
        rows.append(dict(measure=k, n_items=len(p), exact_match=round((p[:, 0] == p[:, 1]).mean(), 3),
                         within_1=round((abs(p[:, 0] - p[:, 1]) <= 1).mean(), 3),
                         mean_abs_diff=round(abs(p[:, 0] - p[:, 1]).mean(), 2),
                         krippendorff_alpha_interval=round(ag.alpha(p, "interval"), 3),
                         spearman=round(spearmanr(p[:, 0], p[:, 1])[0], 3)))
    for k in ["validity", "stride_primary", "tier", "evidence", "is_enabler"]:
        rows.append(dict(measure=k, n_items=len(ids),
                         exact_match=round(np.mean([r1[i].get(k) == r2[i].get(k) for i in ids]), 3)))
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    if a.out: df.to_csv(a.out, index=False)

if __name__ == "__main__":
    main()
