# SPEAR VALIDATION STATUS

## Current state: MODAL GATE CLOSED; NONLINEAR VALIDATION PENDING

SPEAR-M0 v1.0 must not be described as physically validated.

### Required gates

- [x] Executable full 3D modal SPEAR-M0 model
- [x] Modal analysis completed
- [x] Quantitative modal comparison with EFCP targets
- [ ] Pushover +X
- [ ] Pushover -X
- [ ] Pushover +Y
- [ ] Pushover -Y
- [ ] Quantitative comparison with published pushover references
- [ ] Directional asymmetry checked

### Modal targets

| Mode | EFCP target (s) | ETCP reference (s) | OpenSees M0 (s) | Error vs EFCP |
|---|---:|---:|---:|---:|
| 1 | 0.559 | 0.570 | 0.567297 | +1.48% |
| 2 | 0.476 | 0.484 | 0.494985 | +3.99% |
| 3 | 0.385 | 0.392 | 0.386447 | +0.38% |

### Current nonlinear blockers

1. Nonlinear beam macroelements must reproduce the published one-component moment-rotation formulation.
2. Distributed-plasticity fibre columns must be implemented with the published expected material characteristics and reinforcement.
3. First nonlinear validation target is pushover +X; modal parameters are frozen and must not be re-tuned.

No FVD, optimization, NLTHA/MSA or FEMA P-58 work is permitted until the validation gates above are passed.
