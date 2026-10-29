# SPEAR-M0 engineering acceptance

Date: 2026-10-29  
Branch: `spear-jeong-elnashai-m0`

## Decision

**ACCEPTED as an engineering benchmark for the FVD/PBEE research scope.**

This decision evaluates global physical fidelity rather than exact pointwise
reproduction of MAE 04-03 Fig. 2.8. It does not claim recovery of the original
UIUC ZeusNL input deck.

## Acceptance criteria

- first four elastic periods: absolute error no greater than 10%;
- peak base shear in each unidirectional pushover: absolute error no greater
  than 15%;
- all four published spatial load patterns pass equilibrium/torque auditing;
- Y is stronger than X on average and `yn100` is stronger than `yp100`,
  preserving the governing physical contribution of C6;
- no parameter is calibrated solely to match the reference curves.

## Results

| Mode | Published (s) | Model (s) | Error | Gate |
|---:|---:|---:|---:|:---:|
| 1 | 0.510 | 0.51446 | +0.87% | PASS |
| 2 | 0.460 | 0.44775 | -2.66% | PASS |
| 3 | 0.400 | 0.37304 | -6.74% | PASS |
| 4 | 0.180 | 0.17797 | -1.13% | PASS |

| Case | Published peak (kN) | Model peak (kN) | Error | Gate |
|---|---:|---:|---:|:---:|
| +X | 354.363 | 349.132 | -1.48% | PASS |
| -X | 367.335 | 357.950 | -2.55% | PASS |
| +Y | 392.689 | 435.569 | +10.92% | PASS |
| -Y | 454.009 | 464.394 | +2.29% | PASS |

## Retained limitations

- Pre-peak secant stiffness is 18--27% higher than the digitized reference.
- Peak displacement and post-peak curve shape are not reproduced exactly.
- The exact ZeusNL `con2` tensile input, original beam gravity load-point
  ledger and dimensioned bent-bar transition were not publicly recoverable.
- These uncertainties must be reported in publications and considered when
  interpreting absolute nonlinear demand, but are no longer project blockers.

The executable gate is
`validation/check_spear_m0_engineering_acceptance.py`; its machine-readable
result is `results/SPEAR/jeong_elnashai/engineering_acceptance.json`.

## Authorized next stage

The frozen M0 baseline may now be used to develop the FVD retrofit model and
to run baseline nonlinear response-history analyses. Optimization, MSA and
FEMA P-58 remain subsequent stages and must use separately documented gates.
