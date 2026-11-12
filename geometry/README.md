# Geometry simulations (stealth window, per-satellite gain, dropped reports)

Illustrative analysis of the effect of a covert range bias on the horizontal error of a multilateration solution in assumed Walker-Star constellations (200 satellites, 500 km, inclination 86 deg, aircraft at 10 km; the SATERA constellation is not fully published). Results are quoted in the supplementary material of the manuscript (subsection *Per-Satellite Gains, Actual Errors and the Four Transfer Channels*) and in the workbook sheet *Geometry Gains*.

| File | What it does | Output |
|---|---|---|
| `hdop.py`, `hdop2.py` | constellation, visibility, HDOP and per-satellite gain | library (also usable from the command line: `python hdop.py P S F mask_deg`) |
| `hdop3.py` | HDOP and gain statistics for variants A to E; adversarial dropping | `hdop_results.json` |
| `gain.py` | gain g_i (horizontal norm of column i of K = (G'G)^-1 G'), leverage, RAIM-style residual test, actual error of a 30 m step, shares above h* = 350/30 | `gain_results.json` |
| `gain2.py` | Monte-Carlo check of the linear model (40 geometries, 4,000 draws each; seed 7); reports dropped to m = 3, 4, 6 | `gain2_results.json` |
| `gain3.py` | share of samples with an open stealth window for k = 1, 2, 4 and sigma = 10, 30, 100 m | `gain3_results.json` |

Parameters are named constants at the top of each script: variants (planes x satellites per plane, phasing, elevation limit), aircraft altitude, latitude/longitude/epoch grid, `EREQ` = 350 m, `STEP` = 30 m, `SIG`, `PFA` = 1e-3, random seeds 1 (hdop3) and 7 (gain2). `gain.py` runs its analysis on import (it has no `__main__` guard). Requirements: numpy, scipy.

```
cd geometry && python hdop3.py && python gain.py && python gain2.py && python gain3.py   # about 2 min
```

Assumptions that are not results: the residual test is the textbook chi-square test with n-3 degrees of freedom, not the monitor of SATERA (its threshold is not published); sigma is varied; the requirement of 350 m is used as the bound on the error of a single solution, and the statistic (RMS, percentile or maximum) of the standard is to be confirmed before any share is quoted outside the paper.
