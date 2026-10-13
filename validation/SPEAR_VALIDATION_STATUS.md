# SPEAR VALIDATION STATUS

Date: 2026-10-13
Branch: `spear-jeong-elnashai-m0`

## Current state: MODAL CHECK RUN; PUSHOVER PATTERN SOURCE-LOCKED; NONLINEAR INPUTS PENDING

SPEAR-M0 is not physically validated and must not be used for FVD, optimization,
NLTHA/MSA or FEMA P-58.

## Actions completed in this pass

- Audited the Jeong-Elnashai pushover driver and identified an inadmissible
  automatic selection of the lateral pushover mode by effective modal mass.
- Removed that selection from the validation workflow. MAE 04-03 Section 2.3.1
  requires lateral force distribution proportional to first mode shape and mass
  distribution, followed by the Fig. 2.7 plan redistribution.
- Implemented the source-locked unidirectional cases `xp100`, `xn100`, `yp100`,
  `yn100` using Fig. 2.7 fractions.
- Digitized the supplied Fig. 2.8 image as a machine-readable reference curve.
- Re-ran the executable modal model without stiffness or mass calibration.
- Wrote reproducible run outputs under `results/SPEAR/jeong_elnashai/`.

## Modal comparison

| Mode | MAE 04-03 target (s) | OpenSeesPy M0 (s) | Error |
|---:|---:|---:|---:|
| 1 | 0.510 | 0.543523 | +6.57% |
| 2 | 0.460 | 0.466114 | +1.33% |
| 3 | 0.400 | 0.356272 | -10.93% |
| 4 | 0.180 | 0.182575 | +1.43% |

## Pushover gate

Not executed for acceptance in this pass.

The previous implementation selected a lateral mode automatically from modal
effective mass. That is not the MAE 04-03 procedure and can hide modeling errors
in an irregular torsionally coupled frame.

Source-locked pattern rule now used:

- Floor distribution: `Fi = V * phi_i * m_i / sum(phi_i * m_i)`, using the first
  mode shape as stated in MAE 04-03 Eq. 2.5.
- X plan redistribution from Fig. 2.7: `0.24 Vx`, `0.50 Vx`, `0.26 Vx`.
- Y plan redistribution from Fig. 2.7: `0.15 Vy`, `0.44 Vy`, `0.41 Vy`.

Required source data before running nonlinear acceptance pushover:

- Complete beam reinforcement by member and storey.
- Complete column reinforcement by member and storey.
- Exact Fig. 2.6 nodal gravity and seismic mass allocation at beam-column
  connections.

## Required gates

- [x] Executable 3D modal model
- [x] Modal periods computed against MAE 04-03 targets
- [ ] Mode-shape comparison documented quantitatively
- [ ] Source-locked gravity and nodal mass allocation
- [ ] Source-locked member reinforcement
- [x] Published lateral pushover patterns implemented
- [ ] Pushover +X (`xp100`)
- [ ] Pushover -X (`xn100`)
- [ ] Pushover +Y (`yp100`)
- [ ] Pushover -Y (`yn100`)
- [x] Fig. 2.8 reference curve digitized
- [ ] Quantitative Fig. 2.8 curve comparison against OpenSees results

## Reproducibility note

In this runtime, OpenSeesPy 3.8.0.0 requires:

```bash
MPICH_INTERFACE_HOSTNAME=127.0.0.1 python models/SPEAR/jeong_elnashai/spear_m0_jeong_elnashai.py
```

Without that environment variable, MPI initialization fails before model
construction.
