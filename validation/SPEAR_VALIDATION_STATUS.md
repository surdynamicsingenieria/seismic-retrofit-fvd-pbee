# SPEAR VALIDATION STATUS

Date: 2026-10-14
Branch: `spear-jeong-elnashai-m0`

## Current state: FIBRE T-BEAM DIAGNOSTIC RUN; GRAVITY/MASS INPUTS PENDING

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
- Replaced the elastic beams with source-locked 250 x 500 mm fibre T-sections,
  individual published effective flange widths, and the Fig. 2.3 typical
  bent-bar layout using five Gauss-Lobatto integration points.
- Re-ran all four pushover cases. Three reached 200 mm; `yn100` reached
  -53.33 mm and then failed force-based element compatibility convergence.

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

- Exact Fig. 2.6 nodal gravity and seismic mass allocation at beam-column
  connections.
- Resolve the source-consistent `yn100` post-peak convergence failure without
  modifying physical parameters.

## Diagnostic pushover comparison

The fibre T-beam diagnostic materially reduced Y-direction capacity. The X
cases remain too strong; `yp100` remains too strong; and `yn100` is incomplete,
so its apparent peak error is not an acceptance metric.

| Case | Fig. 2.8 Vmax (kN) | Diagnostic Vmax (kN) | Peak error |
|---|---:|---:|---:|
| `xp100` | 354.363 | 515.176 | +45.38% |
| `xn100` | 367.335 | 509.977 | +38.83% |
| `yp100` | 392.689 | 639.248 | +62.79% |
| `yn100` | 454.009 | 509.052* | +12.12%* |

`* yn100` stopped at -53.33 mm, before the reference peak at -147.74 mm.
The comparison has only 55 common digitized points and is incomplete.

The current fibre model periods are 0.57437, 0.50643, 0.37823 and 0.18678 s.
Their deviation from both the published periods and the separate elastic modal
baseline shows that nonlinear section initial stiffness/material assumptions
must be audited together with the unresolved nodal mass ledger; they are not
to be calibrated.

## Required gates

- [x] Executable 3D modal model
- [x] Modal periods computed against MAE 04-03 targets
- [ ] Mode-shape comparison documented quantitatively
- [ ] Source-locked gravity and nodal mass allocation
- [x] Source-locked member reinforcement data from Fig. 2.3
- [x] Diagnostic fibre implementation of the Fig. 2.3 bent-bar beam layout
- [x] Published lateral pushover patterns implemented
- [x] Diagnostic pushover +X (`xp100`)
- [x] Diagnostic pushover -X (`xn100`)
- [x] Diagnostic pushover +Y (`yp100`)
- [ ] Diagnostic pushover -Y (`yn100`) to full target (currently -53.33 mm)
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
