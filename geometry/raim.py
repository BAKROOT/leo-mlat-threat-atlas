"""RAIM-style integrity model and stealth window Omega = Omega_L1 ∩ Omega_L3 (assumed monitor model).

The SATERA integrity monitor (A3.4) is not published. This script ASSUMES the textbook
least-squares residual (chi-square) test of receiver autonomous integrity monitoring:

  measurement model   y = G x + e,  e ~ N(0, sigma^2 I),  rows of G = [-u_e, -u_n, 1]
                      (unknowns: east, north, emission-time term; aircraft altitude known)
  test statistic      q = |(I - H) y|^2 / sigma^2 ~ chi2(n-3)            (fault-free)
  threshold           q > T2 = k^2 * chi2.ppf(1 - P_FA, n-3)             (k = 1 nominal; k > 1 relaxed, T3.06)
  bias b on sat. i    q ~ noncentral chi2(n-3, lam), lam = b^2 (1 - h_ii) / sigma^2
  lam_det             noncentrality at which P(q < T2) = P_MD
  MDB_i               sigma * sqrt(lam_det / (1 - h_ii))                  (minimum detectable bias)
  slope_i             g_i / sqrt(1 - h_ii)                                (horizontal error per unit test statistic)
  HPL_i               sigma * sqrt(lam_det) * slope_i = g_i * MDB_i       (horizontal protection level)

Stealth window of satellite i (range-equivalent bias eps on that satellite only):
  Omega_L3,i = [ e_req / g_i , MDB_i )      non-empty  <=>  HPL_i > e_req
  Omega_L1   = [ 0 , eps_L1 ]               eps_L1 = largest step that escapes the L1 clock checks
  Omega_i    = Omega_L3,i ∩ Omega_L1        non-empty  <=>  HPL_i > e_req  and  g_i * eps_L1 >= e_req
With n = 3 there is no redundancy: MDB_i = inf and only the L1 bound and the gain limit the bias.

eps_L1 is not published; under assumption W1 a covert 100 ns step (about 30 m) escapes the clock
checks, so eps_L1 = 30 m is used as the bias available to the clock route without an L1 enabler.
Geometry: assumed Walker-Star variants of hdop2.geom (200 satellites, 500 km, 86 deg).
Output: raim_results.json.  Requirements: numpy, scipy.  Seed 7.  Run time about 2-4 min.
"""
import numpy as np, json
from scipy.stats import chi2, ncx2
from scipy.optimize import brentq
from hdop2 import geom

EREQ = 350.0          # m, en-route horizontal requirement used as the bound on one solution
EPS_L1 = 0.2998 * 100 # m, the covert 100 ns step (W1)
P_FA, P_MD = 1e-3, 1e-3
SIGMAS = (10.0, 30.0, 100.0)
KS = (1.0, 2.0, 4.0)  # threshold relaxation factor (C channel, T3.06)
rng = np.random.default_rng(7)

_lam = {}
def lam_det(dof, k=1.0):
    key = (dof, k)
    if key not in _lam:
        T2 = k * k * chi2.ppf(1 - P_FA, dof)
        _lam[key] = brentq(lambda l: ncx2.cdf(T2, dof, l) - P_MD, 1e-6, 1e5)
    return _lam[key]

def analyse(E, N):
    G = np.column_stack([-E, -N, np.ones(len(E))]); K = np.linalg.pinv(G)
    g = np.sqrt((K[:2] ** 2).sum(0)); hii = np.clip(np.diag(G @ K), 0, 1)
    return g, hii

def window(g, hii, n, sigma, k=1.0, eps_l1=EPS_L1):
    """returns (L3 window open for some sat, L1∩L3 open for some sat, max HPL)"""
    if n <= 3:
        mdb = np.full(n, np.inf)
    else:
        mdb = sigma * np.sqrt(lam_det(n - 3, k) / np.clip(1 - hii, 1e-12, 1))
    lo = EREQ / np.maximum(g, 1e-12)
    l3 = lo < mdb
    both = l3 & (lo <= eps_l1)
    hpl = np.max(g * mdb)
    return bool(l3.any()), bool(both.any()), float(hpl)

VARIANTS = {'A 10x20, 0deg': (10, 20, 1, 0.0), 'B 10x20, 5deg': (10, 20, 1, 5.0),
            'C 20x10, 0deg': (20, 10, 1, 0.0), 'D 8x25, 0deg': (8, 25, 1, 0.0)}

def summarise(recs):
    gmax = np.array([r[1].max() for r in recs]); hd = np.array([np.sqrt((r[1] ** 2).sum()) for r in recs])
    d = {'samples': len(recs), 'n_med': float(np.median([r[0] for r in recs])),
         'hdop_med': float(np.median(hd)), 'hdop_p99': float(np.percentile(hd, 99)),
         'gmax_med': float(np.median(gmax)), 'gmax_p99': float(np.percentile(gmax, 99)), 'gmax_max': float(gmax.max()),
         'err_l1step_max_m': float(gmax.max() * EPS_L1),
         'share_hdop_gt_hstar': float(np.mean(hd > EREQ / EPS_L1)), 'share_gmax_gt_gstar': float(np.mean(gmax > EREQ / EPS_L1)),
         'eps_breach_min_m': float(np.min(EREQ / gmax))}
    for s in SIGMAS:
        for k in KS:
            o3 = ob = 0; hpl = []
            for n, g, hii in recs:
                a, b, h = window(g, hii, n, s, k); o3 += a; ob += b; hpl.append(h)
            d[f'sig{int(s)}_k{int(k)}'] = {'omega_L3_open': o3 / len(recs), 'omega_open': ob / len(recs),
                                           'hpl_med_m': float(np.median(hpl))}
    return d

def main():
    res = {'assumptions': {'EREQ_m': EREQ, 'EPS_L1_m': EPS_L1, 'P_FA': P_FA, 'P_MD': P_MD, 'sigma_m': SIGMAS, 'k': KS,
                           'lam_det': {str(d): lam_det(d) for d in range(1, 13)}}}
    for name, (P, S, F, m) in VARIANTS.items():
        recs = []
        for l, E, N in geom(P, S, F, m):
            if len(E) >= 3:
                g, hii = analyse(E, N); recs.append((len(E), g, hii))
        res[name] = summarise(recs)
        print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[name].items() if not isinstance(v, dict)})
        print('   ', {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in res[name].items() if isinstance(v, dict) and k.endswith('k1')})

    # T2.04: reports dropped so that m remain, adversarial choice over random m-subsets (variant A)
    rows = [r for r in geom(10, 20, 1, 0.0)]
    sel = rng.permutation(len(rows))[:1200]
    for mkeep in (6, 4, 3):
        out = {s: {k: [0, 0] for k in KS} for s in SIGMAS}; gm = []; hw = []; tot = 0
        for i in sel:
            l, E, N = rows[i]; n = len(E)
            if n < mkeep: continue
            tot += 1; best = {s: {k: [False, False] for k in KS} for s in SIGMAS}; gbest = 0; hbest = 0
            for _ in range(400):
                c = rng.choice(n, mkeep, replace=False)
                g, hii = analyse(E[c], N[c]); gbest = max(gbest, g.max()); hbest = max(hbest, float(np.sqrt((g ** 2).sum())))
                for s in SIGMAS:
                    for k in KS:
                        a, b, _ = window(g, hii, mkeep, s, k)
                        best[s][k][0] |= a; best[s][k][1] |= b
            gm.append(gbest); hw.append(hbest)
            for s in SIGMAS:
                for k in KS:
                    out[s][k][0] += best[s][k][0]; out[s][k][1] += best[s][k][1]
        gm = np.array(gm); hw = np.array(hw)
        d = {'samples': tot, 'gmax_worst_med': float(np.median(gm)), 'share_gmax_gt_gstar': float(np.mean(gm > EREQ / EPS_L1)),
             'hdop_worst_med': float(np.median(hw)), 'hdop_worst_p95': float(np.percentile(hw, 95)),
             'err_l1step_worst_med_m': float(np.median(gm) * EPS_L1)}
        for s in SIGMAS:
            d[f'share_sigma_hdop_gt_ereq_sig{int(s)}'] = float(np.mean(hw * s > EREQ))
        for s in SIGMAS:
            for k in KS:
                d[f'sig{int(s)}_k{int(k)}'] = {'omega_L3_open': out[s][k][0] / tot, 'omega_open': out[s][k][1] / tot}
        res[f'A 10x20, 0deg, T2.04 keeps {mkeep}'] = d
        print('keep', mkeep, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items() if not isinstance(v, dict)},
              {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in d.items() if isinstance(v, dict) and k.endswith('k1')})
    json.dump(res, open('raim_results.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
