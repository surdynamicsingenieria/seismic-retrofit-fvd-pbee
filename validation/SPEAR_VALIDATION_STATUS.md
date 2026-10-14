# SPEAR VALIDATION STATUS

Date: 2026-10-14
Branch: `spear-jeong-elnashai-m0`

## Current state: DIAGNOSTIC PUSHOVER RUN; NONLINEAR INPUTS PENDING

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
- Ran diagnostic pushover in all four directions to +/-200 mm.
- Compared the diagnostic curves against the digitized Fig. 2.8 reference.
- Re-ran the executable modal model without stiffness or mass calibration.
- Source-locked the Fig. 2.3 reinforcement data in code and corrected the
  diagnostic column cover from 31 mm to the published 15 mm.
- Added the full digitized Fig. 2.8 CSV to the repository, so the comparison
  script no longer depends on an untracked local reference file.
- Extended the Fig. 2.8 comparison utility to emit an SVG plot.
- Wrote reproducible run outputs under `results/SPEAR/jeong_elnashai/`.

## Modal comparison

| Mode | MAE 04-03 target (s) | OpenSeesPy M0 (s) | Error |
|---:|---:|---:|---:|
| 1 | 0.510 | 0.543523 | +6.57% |
| 2 | 0.460 | 0.466114 | +1.33% |
| 3 | 0.400 | 0.356272 | -10.93% |
| 4 | 0.180 | 0.182575 | +1.43% |

## Pushover gate

Executed only as a diagnostic run, not an acceptance run.

The previous implementation selected a lateral mode automatically from modal
effective mass. That is not the MAE 04-03 procedure and can hide modeling errors
in an irregular torsionally coupled frame.

Source-locked pattern rule now used:

- Floor distribution: `Fi = V * phi_i * m_i / sum(phi_i * m_i)`, using the first
  mode shape as stated in MAE 04-03 Eq. 2.5.
- X plan redistribution from Fig. 2.7: `0.24 Vx`, `0.50 Vx`, `0.26 Vx`.
- Y plan redistribution from Fig. 2.7: `0.15 Vy`, `0.44 Vy`, `0.41 Vy`.

Required implementation work before running nonlinear acceptance pushover:

- Implement the Fig. 2.3 typical RC T-beam as fibre sections with the published
  bent-bar longitudinal layout. Keeping beams elastic is diagnostic only.
- Exact Fig. 2.6 nodal gravity and seismic mass allocation at beam-column
  connections.

## Diagnostic pushover comparison

The four diagnostic runs completed to +/-200 mm without convergence fallback.
They are too strong relative to Fig. 2.8, which confirms that the remaining
problem is not the lateral pattern definition but the incomplete nonlinear
member model and lumped gravity/mass allocation.

| Case | Fig. 2.8 Vmax (kN) | Diagnostic Vmax (kN) | Peak error |
|---|---:|---:|---:|
| `xp100` | 354.363 | 518.273 | +46.25% |
| `xn100` | 367.335 | 514.301 | +40.01% |
| `yp100` | 392.689 | 703.743 | +79.21% |
| `yn100` | 454.009 | 746.955 | +64.52% |

The source-locked 15 mm cover increased diagnostic strength. That is a valid
physics consequence of the published section geometry, not a calibration step.
The acceptance blocker remains the elastic-beam idealization and simplified
mass/gravity distribution.

## Required gates

- [x] Executable 3D modal model
- [x] Modal periods computed against MAE 04-03 targets
- [ ] Mode-shape comparison documented quantitatively
- [ ] Source-locked gravity and nodal mass allocation
- [x] Source-locked member reinforcement data from Fig. 2.3
- [ ] Fibre implementation of the Fig. 2.3 bent-bar beam layout
- [x] Published lateral pushover patterns implemented
- [x] Diagnostic pushover +X (`xp100`)
- [x] Diagnostic pushover -X (`xn100`)
- [x] Diagnostic pushover +Y (`yp100`)
- [x] Diagnostic pushover -Y (`yn100`)
- [x] Fig. 2.8 reference curve digitized
- [x] Quantitative Fig. 2.8 curve comparison against diagnostic OpenSees results
- [ ] Acceptance pushover with source-locked reinforcement and Fig. 2.6 mass/loading

## Reproducibility note

In this runtime, OpenSeesPy 3.8.0.0 requires:

```bash
MPICH_INTERFACE_HOSTNAME=127.0.0.1 python models/SPEAR/jeong_elnashai/spear_m0_jeong_elnashai.py
MPICH_INTERFACE_HOSTNAME=127.0.0.1 python models/SPEAR/jeong_elnashai/spear_m0_jeong_elnashai_nonlinear.py
python validation/compare_pushover_to_fig_2_8.py
```

Without that environment variable, MPI initialization fails before model
construction.
