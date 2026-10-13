# SPEAR VALIDATION STATUS

Date: 2026-10-13
Branch: `spear-jeong-elnashai-m0`

## Current state: MODAL CHECK RUN; PUSHOVER BLOCKED BY SOURCE DATA

SPEAR-M0 is not physically validated and must not be used for FVD, optimization,
NLTHA/MSA or FEMA P-58.

## Actions completed in this pass

- Audited the Jeong-Elnashai pushover driver and identified an inadmissible
  automatic selection of the lateral pushover mode by effective modal mass.
- Removed that selection from the validation workflow: pushover acceptance must
  use the four published study patterns `xp100`, `xn100`, `yp100`, `yn100`, not a
  post-hoc modal participation rule.
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
effective mass. That is not a source-locked Jeong-Elnashai pushover pattern and
can hide modeling errors in an irregular torsionally coupled frame.

Required source data before running acceptance pushover:

- Exact lateral load vectors or textual definition for `xp100`, `xn100`, `yp100`,
  `yn100` from MAE 04-03.
- Digitized Fig. 2.8 curves, stored as machine-readable reference data.
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
- [ ] Published lateral pushover patterns implemented
- [ ] Pushover +X (`xp100`)
- [ ] Pushover -X (`xn100`)
- [ ] Pushover +Y (`yp100`)
- [ ] Pushover -Y (`yn100`)
- [ ] Quantitative Fig. 2.8 curve comparison

## Reproducibility note

In this runtime, OpenSeesPy 3.8.0.0 requires:

```bash
MPICH_INTERFACE_HOSTNAME=127.0.0.1 python models/SPEAR/jeong_elnashai/spear_m0_jeong_elnashai.py
```

Without that environment variable, MPI initialization fails before model
construction.
