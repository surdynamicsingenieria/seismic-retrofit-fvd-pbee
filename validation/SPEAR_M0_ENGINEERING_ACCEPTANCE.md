# SPEAR-M0 engineering acceptance

Date: 2026-11-05
Branch: `spear-jeong-elnashai-m0`

## Decision

**ACCEPTED WITH DOCUMENTED LIMITATIONS as an engineering benchmark for the
FVD/PBEE research scope.**

This decision evaluates global physical fidelity rather than exact pointwise
reproduction of MAE 04-03 Fig. 2.8. It does not claim recovery of the original
UIUC ZeusNL input deck.

## Acceptance criteria

- first four elastic periods: absolute error no greater than 10%;
- peak base shear in each unidirectional pushover: absolute error no greater
  than 20%;
- all four published spatial load patterns pass equilibrium/torque auditing;
- Y is stronger than X on average and `yn100` is stronger than `yp100`,
  preserving the governing physical contribution of C6;
- no parameter is calibrated solely to match the reference curves.

## Results

| Mode | Published (s) | Model (s) | Error | Gate |
|---:|---:|---:|---:|:---:|
| 1 | 0.510 | 0.49038 | -3.85% | PASS |
| 2 | 0.460 | 0.43323 | -5.82% | PASS |
| 3 | 0.400 | 0.36199 | -9.50% | PASS |
| 4 | 0.180 | 0.17183 | -4.54% | PASS |

| Case | Published peak (kN) | Model peak (kN) | Error | Gate |
|---|---:|---:|---:|:---:|
| +X | 354.363 | 328.071 | -7.42% | PASS |
| -X | 367.335 | 324.002 | -11.80% | PASS |
| +Y | 392.689 | 351.817 | -10.41% | PASS |
| -Y | 454.009 | 367.537 | -19.05% | PASS |

## Retained limitations

- The source-correct Section 2 model has no rigid diaphragm; the previous
  accepted result used a later Section 5.2 refinement and is superseded.
- Peak displacement and post-peak curve shape are not reproduced exactly.
- The exact ZeusNL `con2` tensile input, original beam gravity load-point
  ledger and dimensioned bent-bar transition were not publicly recoverable.
- These uncertainties must be reported in publications and considered when
  interpreting absolute nonlinear demand, but are no longer project blockers.

The executable gate is
`validation/check_spear_m0_engineering_acceptance.py`; its machine-readable
result is `results/SPEAR/jeong_elnashai/engineering_acceptance.json`.

## Downstream decision

Baseline NLTHA and FVD model development are authorized. Optimization, MSA and
FEMA P-58 remain closed until separate downstream gates are documented. The
modal gate and all qualitative mechanism checks pass, including the published
+Y first/second-storey drift similarity. The -Y peak-strength error of -19.05%
must be propagated as model-form uncertainty and stated in publications.
