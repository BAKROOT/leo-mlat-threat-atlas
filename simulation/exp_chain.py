"""E3. End-to-end attack chains over time, with the L3 monitor, the ADS-B cross-check and two candidate defences.

Assumed model (see sim_core.py): variant A (10 x 20, 0 deg), aircraft en route at 10 km and 250 m/s on random headings,
one report per satellite in view per second, range error sigma = 30 m, residual clock error of every satellite
N(0, 2 m) (the noise floor of the clock filter of exp_l1.py), 10-min runs.

Attacks (on one target aircraft and one satellite s*, the one in view for the whole run that the adversary can make
dominant):
  clock         : a bias eps_L1 = 31 m on the clock of s*, the largest induced by the joint attack T1.11 and T2.06 in
                  exp_l1.py that raises no clock alarm (single-input attacks induce under 1 m);
  T2.04 (m)     : only m reports of the target are delivered (s* and the m-1 others that make s* dominant; the subset
                  is re-chosen every 10 s from 60 random candidates);
  T2.01         : a bias on the observables of s* set each second to half the minimum detectable bias (the stealthiest
                  bias that still has a chance to breach), not bounded by any clock check;
  T3.06 (k)     : residual threshold raised by k.
Detection layers:
  L3 residual   : chi-square test, P_FA 1e-3 per solution;
  cross-check   : |MLAT - ADS-B| > T_x with T_x = 500 m or 1852 m (1 NM); not available for a target without ADS-B;
  D1 (defence)  : protection-level alarm, integrity flagged unavailable when HPL > e_req (P_MD 1e-3);
  D2 (defence)  : dropped-report monitor: over the last 10 s, the number of missing reports of satellites in view
                  exceeds the binomial (1 - 1e-4) quantile of a nominal random loss of 5 per cent.
Output: results_chain.json; one row per scenario with the share of epochs in which the error exceeds 350 m and no
layer flags it, layer by layer, and the share in which the displacement caused by the attack itself (against the same
noise without the injected bias) exceeds 350 m undetected.
"""
import json, numpy as np
from scipy.stats import binom
from sim_core import *

rng = np.random.default_rng(23)
EREQ, SIG, CLK = 350.0, 30.0, 2.0
EPS_L1 = 31.0
NTRAJ, DUR, P_LOSS = 60, 600, 0.05
c = constellation(10, 20, 1)

def trajectory():
    lat0 = np.radians(rng.uniform(-60, 60)); lon0 = rng.uniform(-np.pi, np.pi); hd = rng.uniform(0, 2 * np.pi)
    pts = []; lat, lon = lat0, lon0
    for k in range(DUR):
        pts.append(llh_to_xyz(lat, lon))
        d = 250.0 / (RE + ALT_AC)
        lat += d * np.cos(hd); lon += d * np.sin(hd) / max(np.cos(lat), 1e-3)
    return pts

def gain_of(sp, p, sub, i):
    d = sp[sub] - p; rng_ = np.linalg.norm(d, axis=1); los = d / rng_[:, None]
    lat = np.arcsin(p[2] / np.linalg.norm(p)); lon = np.arctan2(p[1], p[0]); e, n, u = enu_basis(lat, lon)
    G = np.column_stack([-(los @ e), -(los @ n), np.ones(len(sub))])
    g, _ = gains(G); return g[list(sub).index(i)]

SCEN = [('nominal', 0, None, 0, 1), ('clock', EPS_L1, None, 0, 1), ('clock + T2.04 (4)', EPS_L1, 4, 0, 1),
        ('clock + T2.04 (3)', EPS_L1, 3, 0, 1), ('T2.04 (4) alone', 0, 4, 0, 1), ('T2.04 (3) alone', 0, 3, 0, 1),
        ('T2.01', 0, None, 1, 1), ('T2.01 + T3.06 (k=4)', 0, None, 1, 4), ('clock + T3.06 (k=4)', EPS_L1, None, 0, 4)]
thr_d2 = {}
acc = {s[0]: dict(epochs=0, err=0, ind=0, ind_und=0, ind_und_x500=0, ind_und_D1=0, und_L3=0, und_x500=0, und_x1852=0, und_noadsb_L3=0, und_D1=0, d2_alarm=0, d2_first=[], maxerr=[]) for s in SCEN}

for tr in range(NTRAJ):
    pts = trajectory()
    vis0 = [set(visible(sat_pos(c, t), pts[t])) for t in range(DUR)]
    common = set.intersection(*vis0)
    if not common: continue
    clk = rng.normal(0, CLK, len(c))
    sp_mid = sat_pos(c, DUR // 2)
    cand = sorted(common, key=lambda i: -np.linalg.norm(sp_mid[i] - pts[DUR // 2]))[:3]   # low-elevation, long-visible candidates
    for name, eps_clk, mkeep, t201, k in SCEN:
        a = acc[name]; sstar = cand[0]; sub = None; miss_hist = []; first = None; me = 0.0
        for t in range(DUR):
            sp = sat_pos(c, t); p = pts[t]; v = sorted(vis0[t])
            if mkeep:
                if t % 10 == 0 or sub is None or not set(sub) <= set(v):
                    others = [j for j in v if j != sstar]; best, bg = None, -1
                    for _ in range(60):
                        s = [sstar] + list(rng.choice(others, mkeep - 1, replace=False))
                        gg = gain_of(sp, p, s, sstar)
                        if gg > bg: bg, best = gg, s
                    sub = best
                kept = sorted(sub)
            else:
                kept = [j for j in v if rng.random() > P_LOSS] if name == 'nominal' else v
            n = len(kept)
            if n < 3: continue
            rho = np.linalg.norm(sp[kept] - p, axis=1) + clk[kept] + rng.normal(0, SIG, n)
            rho_clean = rho.copy()
            idx = kept.index(sstar) if sstar in kept else None
            if idx is not None and eps_clk: rho[idx] += eps_clk
            if idx is not None and t201:
                _, _, _, G0 = solve(sp[kept], np.linalg.norm(sp[kept] - p, axis=1), p); g, hii = gains(G0)
                if n > 3: rho[idx] += 0.5 * SIG * np.sqrt(lam_det(n - 3, k=k) / (1 - hii[idx]))
                else: rho[idx] += 2 * EREQ / g[idx]
            ph, ct, res, G = solve(sp[kept], rho, p)
            alarm, hpl = monitor(res, G, SIG, k=k)
            err = horiz_dist(ph, p); me = max(me, err)
            # displacement caused by the attack itself: same noise and same reports, without the injected bias
            p0, _, _, _ = solve(sp[kept], rho_clean, p); ind = horiz_dist(ph, p0)
            if ind > EREQ:
                a['ind'] += 1
                if not alarm:
                    a['ind_und'] += 1; a['ind_und_x500'] += err <= 500; a['ind_und_D1'] += hpl <= EREQ
            # D2: missing reports of satellites in view over the last 10 s
            miss_hist.append(len(v) - n); win = miss_hist[-10:]; expn = len(v) * len(win)
            if expn not in thr_d2: thr_d2[expn] = binom.ppf(1 - 1e-4, expn, P_LOSS)
            d2 = sum(win) > thr_d2[expn]
            if d2 and first is None: first = t
            a['epochs'] += 1; a['d2_alarm'] += d2
            if err > EREQ:
                a['err'] += 1
                if not alarm:
                    a['und_L3'] += 1; a['und_noadsb_L3'] += 1
                    xe = err   # honest aircraft: ADS-B is the true position (GNSS error ignored)
                    a['und_x500'] += xe <= 500; a['und_x1852'] += xe <= 1852
                    a['und_D1'] += hpl <= EREQ
        a['d2_first'].append(first); a['maxerr'].append(me)

out = {'assumptions': {'variant': '10x20, 0 deg', 'sigma_m': SIG, 'clock_floor_m': CLK, 'eps_L1_m': EPS_L1,
                       'trajectories': NTRAJ, 'duration_s': DUR, 'nominal_loss': P_LOSS}}
for name, *_ in SCEN:
    a = acc[name]; E = a['epochs']
    f = [x for x in a['d2_first'] if x is not None]
    out[name] = {'epochs': E, 'share_err_gt_350': a['err'] / E,
                 'share_attack_displacement_gt_350': a['ind'] / E, 'share_attack_displacement_undetected_L3': a['ind_und'] / E,
                 'share_attack_displacement_undetected_L3_xcheck_500': a['ind_und_x500'] / E,
                 'share_attack_displacement_undetected_L3_D1': a['ind_und_D1'] / E, 'share_undetected_L3': a['und_L3'] / E,
                 'share_undetected_L3_and_xcheck_500': a['und_x500'] / E, 'share_undetected_L3_and_xcheck_1852': a['und_x1852'] / E,
                 'share_undetected_L3_and_D1': a['und_D1'] / E, 'share_epochs_D2_alarm': a['d2_alarm'] / E,
                 'D2_detected_runs': len(f), 'D2_median_first_alarm_s': float(np.median(f)) if f else None,
                 'max_error_median_m': float(np.median(a['maxerr']))}
    print(name, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in out[name].items()})
json.dump(out, open('results_chain.json', 'w'), indent=1)
