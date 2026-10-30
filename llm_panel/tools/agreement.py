#!/usr/bin/env python3
"""
Agreement between the LLM raters: Krippendorff's alpha AND Kendall's W, side by side.

Usage (from the llm_panel folder, after validate_merge.py has written results/panel_long.csv):
    python tools/agreement.py --long results/panel_long.csv \
        --catalogue ../data/catalogue/SATERA_Extended_Threat_Catalogue.xlsx --out results

What it computes (items = threats, raters = models)
  * Krippendorff's alpha with an interval metric and, for ordinal codes, an ordinal metric.
    Handles missing ratings (e.g. enablers have no D). Thresholds: >= 0.800 reliable,
    0.667-0.800 tentative, < 0.667 not reliable (Krippendorff).
  * Kendall's W (coefficient of concordance) on the rankings of the threats by each rater,
    with the tie correction, chi-square p value, and the mean pairwise Spearman rho
    implied by W. Complete cases only (threats rated by every rater).
  * 95% bootstrap intervals over threats for both statistics.
  * Dimensions: D, R, E, A, Di (strong, weak), S (strong, weak) and the DREAD split
    Impact = D + A and Likelihood = R + E + Di; ordinal codes for tier, evidence and band.
  * Three rater sets: 4 LLMs; the same without Claude (vendor-effect check);
    4 LLMs + the authors' catalogue as a fifth rater.
  * Contested items: threats that need a round-2 look under a stated rule.
Requires: Python 3.9+, pandas, numpy, scipy, openpyxl.
"""
import argparse, os, itertools
import numpy as np
import pandas as pd
from scipy.stats import rankdata, chi2

ORD_TIER = {"T3x": 1, "T3": 2, "T2": 3, "T1c": 4, "T1p": 5}      # same coding as the E score
ORD_EVID = {"P": 0, "E0": 1, "E1": 2, "E2": 3, "E3": 4}
ORD_BAND = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}


# ------------------------------------------------------------------ Krippendorff's alpha
def alpha(M, metric="interval"):
    """M: units x raters array with NaN for missing. Returns alpha or NaN."""
    M = np.asarray(M, float)
    vals = np.unique(M[~np.isnan(M)])
    if len(vals) < 2:
        return np.nan
    idx = {v: i for i, v in enumerate(vals)}
    k = len(vals)
    o = np.zeros((k, k))
    for row in M:
        r = row[~np.isnan(row)]
        m = len(r)
        if m < 2:
            continue
        for a, b in itertools.permutations(range(m), 2):
            o[idx[r[a]], idx[r[b]]] += 1.0 / (m - 1)
    nc = o.sum(1)
    n = nc.sum()
    if n <= 1:
        return np.nan
    v = vals.astype(float)
    if metric == "nominal":
        d = (v[:, None] != v[None, :]).astype(float)
    elif metric == "interval":
        d = (v[:, None] - v[None, :]) ** 2
    elif metric == "ordinal":
        cum = np.cumsum(nc)
        d = np.zeros((k, k))
        for i in range(k):
            for j in range(k):
                lo, hi = min(i, j), max(i, j)
                s = cum[hi] - (cum[lo - 1] if lo > 0 else 0) - (nc[lo] + nc[hi]) / 2.0
                d[i, j] = s ** 2
    else:
        raise ValueError(metric)
    do = (o * d).sum()
    de = (nc[:, None] * nc[None, :] * d).sum()
    if de == 0:
        return np.nan
    return 1.0 - (n - 1) * do / de


# ------------------------------------------------------------------ Kendall's W
def kendall_w(M):
    """M: items x raters, complete cases. Returns (W, chi2, p, n, m, mean_rho)."""
    M = np.asarray(M, float)
    M = M[~np.isnan(M).any(axis=1)]
    n, m = M.shape
    if n < 3 or m < 2:
        return (np.nan,) * 6
    R = np.column_stack([rankdata(M[:, j]) for j in range(m)])
    Ri = R.sum(1)
    S = ((Ri - Ri.mean()) ** 2).sum()
    T = 0.0
    for j in range(m):
        _, c = np.unique(M[:, j], return_counts=True)
        T += (c ** 3 - c).sum()
    denom = m ** 2 * (n ** 3 - n) - m * T
    if denom <= 0:
        return (np.nan,) * 6
    W = 12 * S / denom
    x2 = m * (n - 1) * W
    p = chi2.sf(x2, n - 1)
    rho = (m * W - 1) / (m - 1)
    return W, x2, p, n, m, rho


def boot(M, fn, B=1000, seed=7):
    rng = np.random.default_rng(seed)
    M = np.asarray(M, float)
    out = []
    for _ in range(B):
        s = M[rng.integers(0, len(M), len(M))]
        v = fn(s)
        if v == v:
            out.append(v)
    return (np.percentile(out, 2.5), np.percentile(out, 97.5)) if len(out) > 50 else (np.nan, np.nan)


def band_alpha_label(a):
    if a != a: return "n/a"
    return "reliable" if a >= 0.80 else ("tentative" if a >= 0.667 else "not reliable")


def band_w_label(w):
    # scale used in Delphi studies (e.g. Garcia-Crespo et al. 2010): >=0.7 strong, ~0.5 moderate, <0.3 weak
    if w != w: return "n/a"
    return "strong" if w >= 0.7 else ("moderate" if w >= 0.5 else ("fair" if w >= 0.3 else "weak"))


# ------------------------------------------------------------------ data
def build_matrices(L, models, cat=None):
    """Return {dimension: (items x raters DataFrame, kind)}"""
    L = L.copy()
    L["Impact_strong"] = L["D"] + L["A"]
    L["Likelihood_strong"] = L["R"] + L["E"] + L["Di_strong"]
    L["Likelihood_weak"] = L["R"] + L["E"] + L["Di_weak"]
    L["tier_code"] = L["tier"].map(ORD_TIER)
    L["evidence_code"] = L["evidence"].map(ORD_EVID)
    L["band_code"] = L["band_strong"].map(ORD_BAND)
    dims = {
        "D (damage)": "D", "R (reproducibility)": "R", "E (exploitability)": "E", "A (affected users)": "A",
        "Di strong (discoverability)": "Di_strong", "Di weak": "Di_weak",
        "S strong (PA-DREAD total)": "S_strong", "S weak": "S_weak",
        "Impact strong = D + A": "Impact_strong", "Likelihood strong = R + E + Di": "Likelihood_strong",
        "Likelihood weak": "Likelihood_weak",
        "Tier (ordinal)": "tier_code", "Evidence level (ordinal)": "evidence_code", "Band strong (ordinal)": "band_code",
    }
    out = {}
    for label, c in dims.items():
        P = L.pivot(index="id", columns="model", values=c)[models]
        out[label] = (P, c)
    if cat is not None:
        c5 = cat.copy()
        c5["Impact_strong"] = c5["D"] + c5["A"]
        c5["Likelihood_strong"] = c5["R"] + c5["E"] + c5["Di_strong"]
        c5["Likelihood_weak"] = c5["R"] + c5["E"] + c5["Di_weak"]
        c5["tier_code"] = c5["tier"].map(ORD_TIER)
        c5["evidence_code"] = c5["evidence"].map(ORD_EVID)
        c5["band_code"] = c5["band_strong"].map(ORD_BAND)
        for label, (P, c) in list(out.items()):
            P5 = P.copy()
            P5["catalogue"] = c5[c].reindex(P5.index)
            out[label] = (P, c, P5)
    return out


def load_catalogue(path):
    df = pd.read_excel(path, sheet_name="Catalogue", header=3)
    df = df.rename(columns={"Di strong": "Di_strong", "Di weak": "Di_weak", "S strong": "S_strong", "S weak": "S_weak",
                            "Band strong": "band_strong", "Tier code": "tier", "Evidence": "evidence"})
    df = df.set_index("ID")
    for c in ["D", "R", "E", "A", "Di_strong", "Di_weak", "S_strong", "S_weak"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def stats_for(P, kind_ordinal):
    A_int = alpha(P.values, "interval")
    A_ord = alpha(P.values, "ordinal") if kind_ordinal else np.nan
    W, x2, p, n, m, rho = kendall_w(P.values)
    a_ci = boot(P.values, lambda s: alpha(s, "interval"))
    w_ci = boot(P.values, lambda s: kendall_w(s)[0])
    return dict(alpha_interval=A_int, alpha_ordinal=A_ord, alpha_lo=a_ci[0], alpha_hi=a_ci[1],
                W=W, W_lo=w_ci[0], W_hi=w_ci[1], chi2=x2, p=p, n_items_W=n, n_items_alpha=int((P.notna().sum(1) >= 2).sum()),
                mean_pairwise_rho=rho)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--long", default="results/panel_long.csv")
    ap.add_argument("--catalogue", default="../data/catalogue/SATERA_Extended_Threat_Catalogue.xlsx")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    L = pd.read_csv(a.long)
    models = sorted(L.model.unique())
    cat = load_catalogue(a.catalogue)
    mats = build_matrices(L, models, cat)
    ordinal_dims = {"Tier (ordinal)", "Evidence level (ordinal)", "Band strong (ordinal)"}

    sets = {"4 LLMs": lambda t: t[0],
            "3 LLMs (no Claude)": lambda t: t[0].drop(columns=["claude"]) if "claude" in t[0] else t[0],
            "4 LLMs + catalogue": lambda t: t[2]}
    rows = []
    for dim, t in mats.items():
        for sname, f in sets.items():
            P = f(t)
            s = stats_for(P, dim in ordinal_dims)
            rows.append(dict(dimension=dim, raters=sname, n_raters=P.shape[1], **s))
    R = pd.DataFrame(rows)
    R["alpha_reading"] = R.alpha_interval.map(band_alpha_label)
    R["W_reading"] = R.W.map(band_w_label)
    R["W_minus_alpha"] = R.W - R.alpha_interval

    # leave-one-out (4 LLMs)
    loo = []
    for dim, t in mats.items():
        for m in models:
            P = t[0].drop(columns=[m])
            s = stats_for(P, dim in ordinal_dims)
            loo.append(dict(dimension=dim, left_out=m, alpha_interval=s["alpha_interval"], W=s["W"]))
    LOO = pd.DataFrame(loo)

    # model offsets (mean score): shows calibration differences that alpha sees but W ignores
    off = []
    for dim, t in mats.items():
        if dim in ordinal_dims: continue
        r = {"dimension": dim}
        for m in models:
            r[m] = t[0][m].mean()
        r["catalogue"] = t[2]["catalogue"].mean()
        off.append(r)
    OFF = pd.DataFrame(off)

    # contested items
    P = mats["S strong (PA-DREAD total)"][0]
    rng = P.max(1) - P.min(1)
    ranks = P.rank(pct=True)
    rank_spread = ranks.max(1) - ranks.min(1)
    bands = mats["Band strong (ordinal)"][0]
    band_range = bands.max(1) - bands.min(1)
    imp = mats["Impact strong = D + A"][0]
    lik = mats["Likelihood strong = R + E + Di"][0]
    items = pd.DataFrame({
        "S_range": rng, "S_rank_spread": rank_spread.round(2), "band_range": band_range,
        "impact_range": imp.max(1) - imp.min(1), "likelihood_range": lik.max(1) - lik.min(1),
        "D_range": mats["D (damage)"][0].max(1) - mats["D (damage)"][0].min(1),
        "A_range": mats["A (affected users)"][0].max(1) - mats["A (affected users)"][0].min(1),
        "R_range": mats["R (reproducibility)"][0].max(1) - mats["R (reproducibility)"][0].min(1),
        "Di_range": mats["Di strong (discoverability)"][0].max(1) - mats["Di strong (discoverability)"][0].min(1),
    })
    for m in models:
        items["S_" + m] = P[m]
    items["S_catalogue"] = cat["S_strong"].reindex(items.index)
    items["title"] = cat["Threat"].reindex(items.index)
    # rule: contested if the band differs across models by at least one band AND S range >= 4,
    # or the rank spread is >= 0.5, or impact range >= 4, or likelihood range >= 5
    items["contested"] = ((items.band_range >= 1) & (items.S_range >= 4)) | (items.S_rank_spread >= 0.5) | \
                         (items.impact_range >= 4) | (items.likelihood_range >= 5)
    items = items.sort_values(["contested", "S_range"], ascending=False)

    os.makedirs(a.out, exist_ok=True)
    with pd.ExcelWriter(os.path.join(a.out, "Agreement_alpha_vs_W.xlsx")) as xw:
        R.round(3).to_excel(xw, sheet_name="Alpha_and_W", index=False)
        LOO.round(3).to_excel(xw, sheet_name="Leave_one_out", index=False)
        OFF.round(2).to_excel(xw, sheet_name="Model_offsets", index=False)
        items.reset_index().rename(columns={"id": "ID"}).to_excel(xw, sheet_name="Contested_items", index=False)
    R.round(3).to_csv(os.path.join(a.out, "agreement_alpha_vs_W.csv"), index=False)
    print(R[R.raters == "4 LLMs"][["dimension", "alpha_interval", "alpha_ordinal", "W", "p", "n_items_W", "mean_pairwise_rho"]].round(3).to_string(index=False))
    print("contested items:", int(items.contested.sum()), "of", len(items))


if __name__ == "__main__":
    main()
