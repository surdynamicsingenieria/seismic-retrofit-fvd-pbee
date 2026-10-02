# SPEAR VALIDATION STATUS

## Current state: NOT VALIDATED

SPEAR-M0 v1.0 must not be described as physically validated.

### Required gates

- [ ] Executable full 3D SPEAR-M0 model
- [ ] Modal analysis completed
- [ ] Quantitative modal comparison with EFCP targets
- [ ] Pushover +X
- [ ] Pushover -X
- [ ] Pushover +Y
- [ ] Pushover -Y
- [ ] Quantitative comparison with published pushover references
- [ ] Directional asymmetry checked

### Modal targets

| Mode | EFCP target (s) | ETCP reference (s) | OpenSees M0 (s) | Error vs EFCP |
|---|---:|---:|---:|---:|
| 1 | 0.559 | 0.570 | pending | pending |
| 2 | 0.476 | 0.484 | pending | pending |
| 3 | 0.385 | 0.392 | pending | pending |

### Current blockers

1. Exact beam connectivity/member mapping must be locked from the published SPEAR plan.
2. Member-specific beam longitudinal reinforcement must be transcribed before nonlinear pushover.
3. C6 strong-axis orientation must be explicitly checked against the adopted global axes.

No FVD, optimization, NLTHA/MSA or FEMA P-58 work is permitted until the validation gates above are passed.
