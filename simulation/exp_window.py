"""E1. Does the analytic stealth window (paper Sec. 4.7, geometry/raim.py) predict what a nonlinear solver with noise does?

(a) linearity: noise-free Gauss-Newton solutions reproduce e_h = g_i * eps and the residual norm eps*sqrt(1-h_ii);
(b) calibration: with noise, the residual test has the stated false-alarm rate and misses a bias of the size of the
    minimum detectable bias (MDB) with the stated probability;
(c) prediction: the linear model's probability of success (error > e_req and no alarm) against the Monte-Carlo rate of the
    nonlinear solver, for biases inside the window [e_req/g_i, MDB_i) and just outside it.
Variant A (10 x 20, 0 deg) and the same geometry after T2.04 keeps m = 4 reports.  Seed 11.  Output: results_window.json
"""
import json, numpy as np
from sim_core import *

rng = np.random.default_rng(11)
EREQ, SIG = 350.0, 30.0
c = constellation(10, 20, 1)
NGEO = 80

def sample_geom(m_keep=None):
    while True:
        t = rng.uniform(0, T_ORB); lat = np.radians(rng.uniform(-80, 80)); lon = rng.uniform(-np.pi, np.pi)
        p = llh_to_xyz(lat, lon); sp = sat_pos(c, t); v = visible(sp, p)
        if len(v) < 4: continue
        if m_keep:   # adversary keeps the m-subset that maximises the best gain (best of 200 random subsets)
            best, bg = None, 0
            for _ in range(200):
                sub = rng.choice(v, m_keep, replace=False)
                _, _, _, G = solve(sp[sub], np.linalg.norm(sp[sub] - p, axis=1), p)
                g, _ = gains(G)
                if g.max() > bg: bg, best = g.max(), sub
            v = best
        return p, sp[v]

out = {}
for label, mk in (('A nominal', None), ('A, T2.04 keeps 4', 4)):
    lin_e, lin_r, cal_fa, cal_md, inside, outside = [], [], [], [], [], []
    for gi in range(NGEO):
        p, sp = sample_geom(mk)
        n = len(sp); r0 = np.linalg.norm(sp - p, axis=1)
        _, _, _, G = solve(sp, r0, p); g, hii = gains(G); i = int(np.argmax(g))
        lam = lam_det(n - 3); mdb = SIG * np.sqrt(lam / (1 - hii[i])); lo = EREQ / g[i]
        # (a) linearity, noise free, eps from 10 m to 2 km
        for eps in (10.0, 100.0, 1000.0, 2000.0):
            rho = r0.copy(); rho[i] += eps
            ph, ct, res, _ = solve(sp, rho, p)
            lin_e.append(abs(horiz_dist(ph, p) / (g[i] * eps) - 1)); lin_r.append(abs(np.linalg.norm(res) / (eps * np.sqrt(1 - hii[i])) - 1))
        # (b) calibration
        for _ in range(300):
            ph, ct, res, G2 = solve(sp, r0 + rng.normal(0, SIG, n), p); cal_fa.append(monitor(res, G2, SIG)[0])
            rho = r0 + rng.normal(0, SIG, n); rho[i] += mdb
            ph, ct, res, G2 = solve(sp, rho, p); cal_md.append(not monitor(res, G2, SIG)[0])
        # (c) prediction of the success probability (error > e_req and no alarm) by the linear model
        K = np.linalg.pinv(G); kcol = K[:2, i]; Ch = SIG ** 2 * (K[:2] @ K[:2].T)
        T2 = chi2.ppf(1 - 1e-3, n - 3)
        us = (0.1, 0.5, 0.9) if lo < mdb else ()
        for kind, eps in [('in', lo * (mdb / lo) ** u) for u in us] + [('out_low', 0.5 * lo), ('out_high', 1.5 * mdb)]:
            z = rng.multivariate_normal(kcol * eps, Ch, 4000)
            pred = ncx2.cdf(T2, n - 3, eps ** 2 * (1 - hii[i]) / SIG ** 2) * np.mean(np.hypot(z[:, 0], z[:, 1]) > EREQ)
            succ = 0
            for _ in range(200):
                rho = r0 + rng.normal(0, SIG, n); rho[i] += eps
                ph, ct, res, G2 = solve(sp, rho, p)
                succ += (horiz_dist(ph, p) > EREQ) and (not monitor(res, G2, SIG)[0])
            (inside if kind == 'in' else outside).append((succ / 200, pred))
    d = {'geometries': NGEO, 'linearity_err_max_rel': float(max(lin_e)), 'residual_norm_max_rel': float(max(lin_r)),
         'false_alarm_rate': float(np.mean(cal_fa)), 'missed_at_mdb_rate': float(np.mean(cal_md)),
         'n_cases_inside': len(inside), 'n_cases_outside': len(outside),
         'inside_emp_mean': float(np.mean([a for a, b in inside])) if inside else None,
         'inside_pred_mean': float(np.mean([b for a, b in inside])) if inside else None,
         'inside_absdiff_mean': float(np.mean([abs(a - b) for a, b in inside])) if inside else None,
         'inside_absdiff_max': float(np.max([abs(a - b) for a, b in inside])) if inside else None,
         'outside_emp_mean': float(np.mean([a for a, b in outside])), 'outside_pred_mean': float(np.mean([b for a, b in outside])),
         'outside_absdiff_max': float(np.max([abs(a - b) for a, b in outside]))}
    out[label] = d; print(label, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()})
json.dump(out, open('results_window.json', 'w'), indent=1)
