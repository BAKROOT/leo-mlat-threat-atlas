"""E2. The L1 side of the stealth window: how large a clock bias can an attacker induce without tripping the clock checks?

ASSUMED reconstruction of an onboard clock filter of the kind described by the SATERA synchronisation study (an EKF
fusing GNSS and PTP time with three kinds of check: innovation consistency, measurement compliance, GNSS/PTP
disruption). Its parameters are NOT published; the values below are assumptions and are varied.

  state      x = [offset (m), drift (m/s)]  (range-equivalent), random-walk drift
  inputs     z_g = x + v_g (GNSS, sigma_g),  z_p = x + v_p (PTP, sigma_p), 1 Hz
  check 1    innovation test on each input:  |nu| / sqrt(S) > 4.89  (P_FA 1e-6 per input and epoch)
  check 2    consistency: |mean over W s of (z_g - z_p)| > 4.89 * sqrt((sigma_g^2 + sigma_p^2) / W)
  check 3    drift compliance: |estimated drift| > y_max (oscillator specification)
  attacks    GNSS input biased (T1.11), PTP input biased (T2.06), or both biased together (T1.11 and T2.06);
             bias ramps at rate r (m/s) up to a plateau B (m), starting after the filter has converged.
The induced clock error is (estimated offset - true offset): every timestamp is corrected by it, so it is the bias
that reaches the observables (channel Phi).
Output: results_l1.json (largest induced clock error, averaged over the last 5 min and measured against the same noise
without attack, that raises no alarm in at least 19 of 20 runs).
"""
import json, numpy as np

rng = np.random.default_rng(5)
SG, SP = 9.0, 6.0            # m (30 ns and 20 ns), assumed; [14] reports accuracy of tens of nanoseconds
QX, QY = 0.01, 1e-8          # process noise (m^2/s, m^2/s^3), assumed
W = 60                       # s, consistency window
YMAX = 0.03                  # m/s, drift compliance (1e-10 s/s), assumed
T0, TEND = 600, 1800         # attack start, end of run (s); a pass over one region lasts about 10 min
RUNS = 20
GATE = 4.89                  # per-test P_FA 1e-6, so that a 30-min run has a false-alarm budget of a few per thousand

def run(kind, r, B, ymax=YMAX, w=W, seed=None):
    g = np.random.default_rng(seed)
    x = np.zeros(2); P = np.diag([100.0, 1e-4]); F = np.array([[1, 1], [0, 1]]); Q = np.diag([QX, QY])
    xt = np.zeros(2); diff_hist = []; errs = []; maxerr_before = 0.0
    thr_c = GATE * np.sqrt((SG ** 2 + SP ** 2) / w)
    for t in range(TEND):
        xt = F @ xt + np.array([g.normal(0, np.sqrt(QX)), g.normal(0, np.sqrt(QY))])
        a = min(r * max(0, t - T0), B) if t >= T0 else 0.0
        zg = xt[0] + g.normal(0, SG) + (a if kind in ('gnss', 'joint') else 0.0)
        zp = xt[0] + g.normal(0, SP) + (a if kind in ('ptp', 'joint') else 0.0)
        x = F @ x; P = F @ P @ F.T + Q
        for z, s in ((zg, SG), (zp, SP)):
            S = P[0, 0] + s ** 2; nu = z - x[0]
            if t > 120 and abs(nu) / np.sqrt(S) > GATE: return t, None
            K = P[:, 0] / S; x = x + K * nu; P = P - np.outer(K, P[0, :])
        diff_hist.append(zg - zp)
        if t > 120 and len(diff_hist) >= w and abs(np.mean(diff_hist[-w:])) > thr_c: return t, None
        if t > 120 and abs(x[1]) > ymax: return t, None
        errs.append(x[0] - xt[0])
    return None, float(np.mean(errs[-300:]))

def false_alarms(n=40):
    fa = 0
    for k in range(n):
        t, _ = run('none', 0, 0, seed=1000 + k); fa += t is not None
    return fa / n

RATES = (0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0)
PLATEAUS = (3, 10, 30, 100, 300, 1000)

def largest_undetected(kind, ymax=YMAX, w=W):
    best = (0.0, None)
    for r in RATES:
        for B in PLATEAUS:
            induced = []; alarms = 0
            for k in range(RUNS):
                t, e = run(kind, r, B, ymax, w, seed=k)
                if t is not None: alarms += 1; continue
                _, e0 = run('none', 0, 0, ymax, w, seed=k)          # same noise, no attack
                induced.append(abs(e - e0))
            if alarms <= RUNS // 20 and induced and min(induced) > best[0]: best = (float(min(induced)), (r, B))
    return best

out = {'assumptions': {'sigma_gnss_m': SG, 'sigma_ptp_m': SP, 'q': [QX, QY], 'W_s': W, 'y_max_m_per_s': YMAX,
                       'attack_window_s': TEND - T0, 'runs': RUNS, 'gate': GATE}}
out['false_alarm_share_of_runs'] = false_alarms()
for kind in ('gnss', 'ptp', 'joint'):
    e, rb = largest_undetected(kind)
    out[kind] = {'largest_undetected_clock_error_m': e, 'ns': e / 0.2998, 'rate_plateau': rb}
    print(kind, round(e, 2), 'm', round(e / 0.2998, 1), 'ns', rb)
# sensitivity of the joint attack to the drift-compliance limit and of single-input attacks to the window
out['joint_vs_ymax'] = {str(y): largest_undetected('joint', ymax=y)[0] for y in (0.01, 0.03, 0.1, 0.3)}
out['gnss_vs_W'] = {str(w): largest_undetected('gnss', w=w)[0] for w in (10, 60, 300)}
print(out['false_alarm_share_of_runs'], out['joint_vs_ymax'], out['gnss_vs_W'])
json.dump(out, open('results_l1.json', 'w'), indent=1)
