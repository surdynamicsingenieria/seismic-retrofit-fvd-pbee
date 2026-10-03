# SPEAR-M0 modal closure

## Frozen modal candidate

`models/SPEAR/spear_m0_efcp_plan_fajfar_c6.py`

No additional tuning of masses, elastic modulus, member stiffnesses, or beam effective widths is permitted for modal calibration.

## Final modal comparison

| Mode | OpenSees (s) | EFCP reference (s) | Error |
|---|---:|---:|---:|
| 1 | 0.567297 | 0.559 | +1.48% |
| 2 | 0.494985 | 0.476 | +3.99% |
| 3 | 0.386447 | 0.385 | +0.38% |
| 4 | 0.195753 | 0.195 | +0.39% |
| 5 | 0.157960 | 0.159 | -0.65% |
| 6 | 0.129794 | 0.130 | -0.16% |

Modal participation characterization of the frozen pre-correction model confirms the published family:
M1 predominantly X, M2 predominantly Y, M3 predominantly Rz.

## Decision

Modal gate is CLOSED for reproduction purposes.

The residual +3.99% discrepancy in Mode 2 is retained and reported rather than calibrated away.
Five of six modes lie within approximately +/-1.5% of the EFCP reference.

This closure does NOT mean the full SPEAR-M0 nonlinear model is physically validated.
The next gate is nonlinear pushover validation in +X, -X, +Y, -Y.

## Traceability

- Published-plan geometry variant corrected C4 to x=9.70 m.
- C6 section/rigid-offset footprint is oriented 0.25 m in global X and 0.75 m in global Y.
- General rigid offsets are not introduced.
- First-storey analytical column length remains 3.00 m in the EFCP candidate.
