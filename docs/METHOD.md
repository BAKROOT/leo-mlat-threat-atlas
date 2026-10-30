# Method in one page

The full method is in the paper (Sections 3 and 4). This page gives the vocabulary that the data files use.
Authoritative definitions are in the sheet *Legends* of the catalogue workbook.

## System and layers

LEO MLAT-B is the GNSS-independent surveillance concept of the SATERA reference design: low-Earth-orbit satellites receive aircraft
1090 MHz ADS-B emissions and measure time, frequency and angle of arrival; the reports travel over inter-satellite links and downlinks to a ground
Central Processing Station, where a TDOA/FDOA solver and tracker compute a position, an integrity monitor tests it and an E-MLAT/ADS-B
cross-check compares it with the broadcast position; the result goes to air traffic management (ASTERIX CAT020/021).

| Layer | Content | Assets |
|---|---|---|
| L1 physical and infrastructure | aircraft emission, RF front end, payload processor, onboard clocks, GNSS, satellite bus, ground-station antennas | A1.1 to A1.7 |
| L2 data and communication | observable reports, inter-satellite links, downlink and backhaul, PTP time transfer, telecommands | A2.1 to A2.5 |
| L3 service and processing | association, ephemeris and clock database, solver and tracker, integrity monitor, cross-check, ASTERIX encoder, hosting platform | A3.1 to A3.7 |
| L4 governance and integration | synchronisation policy, orbit determination, key management, configuration and update management, data feed to ATM, the ATM system, personnel and suppliers, mission operations | A4.1 to A4.8 |

27 assets in all. Trust boundaries: **TB0** system perimeter (air interface, delivery to ATM, organisational interface); **TB1** payload and platform / links;
**TB2** links / Central Processing Station; **TB3** processing / governance. Five timing assets cut across all layers.

## STRIDE-tau

STRIDE (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege) plus a seventh category,
**tau (temporal integrity)**: the primary effect is an offset, drift or delay in the time reference of an asset on the timing dependency.
It is separated from Tampering by an *authentication-invariance test*: assume every message is authenticated and ask whether the effect would remain;
if it would, the threat is tau (the effect enters before any report exists). Definitions: sheet *Legends*.

## Goals, adversaries, evidence

* **Goals** (one threat may serve several): *Displacement* (a real aircraft shown at a wrong position with a nominal integrity annotation), *Denial*, *Deception*
  (a fabricated target or a wrong integrity verdict), *Disclosure* (keys, configuration, ephemerides or traffic revealed).
* **Adversary classes** AC1 to AC7 (deceptive or deceived aircraft, RF-local emitter, synchronised multi-emitter, timing adversary, link adversary,
  ground-segment intruder, insider or supplier) and **tiers**: T1p / T1c (individual with commercial SDRs, public tools or custom software), T2 (organised group),
  T3 (state-level actor), T3x (T3 with an insider, or two classes).
* **Evidence** per threat is the highest level among the atlas sources bound to it: E3 observed in operation, E2 demonstrated on real hardware, E1 simulated or proof of
  concept, E0 theoretical or survey, **P** postulated (no published mechanism; retained, not discarded). *Analogue only*: the evidence comes from another system; R is reduced by one level.

## Effect-transfer graphs

Every cross-layer edge carries the boundary it crosses, a transfer function and a detection predicate. Channels: **Phi** (L1 to L2: a clock offset becomes a bias on every observable it
stamps), **M** (L2 to L3: bias becomes position error, ephemeris error enters), **V** (within L3: monitor and cross-check verdict), **P** (L3 to L4: error and verdict become a
consequence), **C** (control: sets a threshold, ephemeris, key or configuration of another edge). *Stealth* becomes a window of effect sizes that depends on constellation geometry:
a *strong pass* is a valid solution with HDOP at most h* and a *weak pass* a valid solution with HDOP above h*, with h* = e_req / (c * delta_cov) = 11.67 (350 m requirement, 100 ns covert step).
The detection level of the integrity monitor is not published; assumptions W1 to W4 (sheet *Legends*) state what is assumed.

## PA-DREAD

Propagation-aware DREAD keeps the five DREAD dimensions, each scored 1 to 5 with 5 the riskier end, and reads each from a named artefact of an earlier stage:

| Dimension | Read from | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|---|
| Damage D | consequence at the L4 root of the attack graph | Displacement | Deception | regional denial or flagged degradation | local denial | Disclosure only |
| Reproducibility R | best evidence among the bound atlas entries | E3 | E2 | E1 | E0 | postulated (one level less if the evidence is analogue only) |
| Exploitability E | tier of the adversary class | T1 public tools | T1 custom software | T2 | T3 | T3 with an insider, or two classes |
| Affected users A | extent of the root event | whole constellation | several footprints | one footprint | several aircraft | one aircraft |
| Discoverability Di | first layer whose check flags the effect | no check flags it | only L4 flags it | L3 | L2 | L1 |

The score S = D + R + E + A + Di (5 to 25) is banded **Low 5 to 9, Medium 10 to 14, High 15 to 19, Critical 20 to 25**, and is computed for a strong and a weak pass wherever the
regime changes the scenario. Chains are scored on a sufficient scenario. Enablers (threats with no consequence of their own) are ranked through the chains they complete and have no D.
The scores are ordinal and the bands specific to this study: a score ranks threats; it does not measure a probability.
