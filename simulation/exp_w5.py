"""E4. Assumption W5: what if the central solver also estimates a clock offset per satellite?

Sonnleitner and Hobiger (NAVIGATION 72(3), 2025) estimate the relative clock offsets of unsynchronised receivers jointly
with the aircraft states. Here the same idea is applied per epoch to a region with many aircraft: unknowns are
(east, north, c*t_emit) of every aircraft and one clock offset per satellite in view, the clock offsets carry a random-walk
prior from the previous epoch (process noise q per second), and the linearised least squares is solved every second.
A step eps is put on the clock of one satellite at t = 60 s. The per-aircraft solver of the paper (W5: timestamps taken as
synchronised) is run on the same data for comparison. Displacement = distance between the solutions with and without
the step (same noise).  Variant A, 40 aircraft in a 3000 km x 3000 km box at 35 deg N, sigma = 30 m, 600 s.
Output: results_w5.json
"""
import json, numpy as np
from sim_core import *

rng = np.random.default_rng(31)
SIG, NA, DUR, T_STEP = 30.0, 40, 600, 60
c = constellation(10, 20, 1)
lat0, lon0 = np.radians(35.0), np.radians(10.0)
ac = [llh_to_xyz(lat0 + rng.uniform(-1, 1) * 1500e3 / RE, lon0 + rng.uniform(-1, 1) * 1500e3 / (RE * np.cos(lat0))) for _ in range(NA)]

def geo(sp, p, v):
    lat = np.arcsin(p[2] / np.linalg.norm(p)); lon = np.arctan2(p[1], p[0]); e, n, u = enu_basis(lat, lon)
    d = sp[v] - p; los = d / np.linalg.norm(d, axis=1)[:, None]
    return np.column_stack([-(los @ e), -(los @ n), np.ones(len(v))])

def run(eps, q, sstar_rank=0):
    clk_prior = {}                       # sat -> (estimate, variance)
    noise_seed = 7
    g = np.random.default_rng(noise_seed)
    disp_joint, disp_w5, clk_est = [], [], []
    sstar = None
    for t in range(DUR):
        sp = sat_pos(c, t)
        vis = [visible(sp, p) for p in ac]
        sats = sorted(set(np.concatenate(vis)))
        if sstar is None:                # the satellite seen by most aircraft
            cnt = {s: sum(s in v for v in vis) for s in sats}; sstar = sorted(cnt, key=lambda s: -cnt[s])[sstar_rank]
        noise = [g.normal(0, SIG, len(v)) for v in vis]
        bias = {s: (eps if (s == sstar and t >= T_STEP) else 0.0) for s in sats}
        # joint solution, with and without the step
        nS = len(sats); col = {s: 3 * NA + k for k, s in enumerate(sats)}
        rows, y1, y0 = [], [], []
        for a, (p, v) in enumerate(zip(ac, vis)):
            G = geo(sp, p, v)
            for r, s in enumerate(v):
                row = np.zeros(3 * NA + nS); row[3 * a:3 * a + 3] = G[r]; row[col[s]] = 1.0
                rows.append(row / SIG); y1.append((noise[a][r] + bias[s]) / SIG); y0.append(noise[a][r] / SIG)
        for s in sats:                   # random-walk prior on each clock offset
            est, var = clk_prior.get(s, (0.0, 25.0)); var = var + q
            row = np.zeros(3 * NA + nS); row[col[s]] = 1 / np.sqrt(var); rows.append(row)
            y1.append(est / np.sqrt(var)); y0.append(clk_prior.get(('nb', s), (0.0, 25.0))[0] / np.sqrt(var))
        A = np.array(rows); x1 = np.linalg.lstsq(A, np.array(y1), rcond=None)[0]; x0 = np.linalg.lstsq(A, np.array(y0), rcond=None)[0]
        cov = np.linalg.inv(A.T @ A)
        for s in sats:
            clk_prior[s] = (x1[col[s]], cov[col[s], col[s]]); clk_prior[('nb', s)] = (x0[col[s]], cov[col[s], col[s]])
        dj = [np.hypot(*(x1[3 * a:3 * a + 2] - x0[3 * a:3 * a + 2])) for a in range(NA)]
        # per-aircraft solution (W5): clocks taken as synchronised
        dw = []
        for a, (p, v) in enumerate(zip(ac, vis)):
            G = geo(sp, p, v); K = np.linalg.pinv(G)
            b = np.array([bias[s] for s in v]); dw.append(np.hypot(*(K[:2] @ b)))
        disp_joint.append(max(dj)); disp_w5.append(max(dw)); clk_est.append(x1[col[sstar]] - x0[col[sstar]] if sstar in col else np.nan)
    dj = np.array(disp_joint); dw = np.array(disp_w5)
    after = slice(T_STEP, DUR)
    absorb = next((k for k in range(T_STEP, DUR) if dj[k] < 0.1 * max(dj[T_STEP:T_STEP + 5].max(), 1e-9)), None)
    return {'eps_m': eps, 'q_m2_per_s': q, 'w5_max_displacement_m': float(dw[after].max()),
            'w5_mean_displacement_m': float(dw[after].mean()),
            'joint_peak_displacement_m': float(dj[after].max()), 'joint_displacement_after_60s_m': float(dj[T_STEP + 60:].max()),
            'joint_time_to_10pct_s': (absorb - T_STEP) if absorb is not None else None}

out = {'assumptions': {'aircraft': NA, 'sigma_m': SIG, 'step_at_s': T_STEP, 'duration_s': DUR, 'region': '3000 km box at 35N'}}
for eps in (31.0, 300.0):
    for q in (0.01, 1.0):
        r = run(eps, q); out[f'eps{int(eps)}_q{q}'] = r; print(r)
json.dump(out, open('results_w5.json', 'w'), indent=1)
