# End-to-end simulation of the chains and of two defences

Testbed for Section 6 of the paper. Every parameter is an **assumption** (the SATERA design parameters, its clock
filter and its integrity monitor are not published); the results show what a design of this kind does, not what
SATERA does. Parameters are named constants at the top of each script.

| Script | What it does | Output |
|---|---|---|
| `sim_core.py` | Walker-Star constellation (200 satellites, 500 km, 86 deg), pseudoranges, Gauss-Newton multilateration at known altitude, chi-square residual test (P_FA 1e-3) and protection level (P_MD 1e-3) | library |
| `exp_window.py` | E1: is the analytic stealth window (`geometry/raim.py`) right? Linearity of the nonlinear solver, false-alarm and missed-detection calibration, predicted against simulated probability of an undetected breach; nominal geometry and after T2.04 keeps 4 reports | `results_window.json` |
| `exp_l1.py` | E2: the L1 side of the window. Reconstructed onboard clock filter (GNSS + PTP, innovation, consistency and drift-compliance checks); largest clock bias induced without an alarm by biasing GNSS (T1.11), PTP (T2.06) or both | `results_l1.json` |
| `exp_chain.py` | E3: attack chains over 10-min flights (clock bias, T2.04, T2.01, T3.06), with the L3 monitor, the ADS-B cross-check and the defences D1 (protection-level alarm) and D2 (dropped-report monitor) | `results_chain.json` |
| `exp_w5.py` | E4: assumption W5. A solver that also estimates one clock offset per satellite from all aircraft in view, against the per-aircraft solver | `results_w5.json` |

```
cd simulation && python exp_window.py && python exp_l1.py && python exp_chain.py && python exp_w5.py   # about 12 min
```
Requirements: numpy, scipy. Seeds are fixed in each script.
