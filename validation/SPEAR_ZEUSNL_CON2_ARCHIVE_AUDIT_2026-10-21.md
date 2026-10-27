# ZEUS-NL con2 archive and source-envelope audit — 2026-10-21

## Outcome

The official MAE Center Google Code archive was inspected reproducibly by
GitHub Actions. The archive contains 647 files, but the public `trunk` has zero
non-SVN files. Therefore the mathematical source implementation of `con2`
cannot be recovered from that archive.

The archived official manual does recover the exact input contract:

- `con2` is a uniaxial constant-confinement concrete model based on Mander et
  al. (1988);
- it has four inputs: compressive strength `fc`, tensile strength `ft`,
  peak/crushing strain `eco`, and constant confinement factor `K`;
- the manual example `20, 2.2, 0.002, 1.2` is generic and is not evidence that
  the 25 MPa SPEAR model used `ft=2.2 MPa`.

The audit workflow is
`.github/workflows/zeusnl-con2-source-audit.yml`. Runs
`39495270040`, `39606752096`, and `39606891177` document the progressive
archive inspection.

## Continuous-envelope sensitivity

A separate, non-accepted diagnostic maps the published MAE 04-03 compression
constraints to OpenSees `ConcreteCM`:

- `f'cc = 1.01 x 25 = 25.25 MPa`;
- `eps_cc = 0.002 x [1 + 5(K-1)] = 0.0021`;
- `Ec = 23.5 GPa`, identical to the source-ledger elastic concrete modulus;
- the ConcreteCM shape parameter `rc=1.33212470296` is obtained from the
  published point `sigma(0.00456)=0.85 f'cc`;
- `ft=0` is retained only as an explicit sensitivity bound because the actual
  SPEAR tensile input remains unknown;
- `xcrn=100` keeps the arbitrary ConcreteCM linear cutoff outside the strain
  range so that the continuous envelope, not a fitted post-peak line, governs.

This is an equivalence sensitivity to published constitutive points, not a
capacity calibration, and it does not replace the production model.

### Modal result

| Mode | Published (s) | Pre-gravity (s) | Error | Post-gravity (s) |
|---:|---:|---:|---:|---:|
| 1 | 0.510 | 0.503755 | -1.22% | 0.536545 |
| 2 | 0.460 | 0.441809 | -3.95% | 0.482776 |
| 3 | 0.400 | 0.369815 | -7.55% | 0.399328 |
| 4 | 0.180 | 0.174258 | -3.19% | 0.180929 |

### Four-direction pushover result

GitHub Actions run `39705499820` completed all four cases to +/-200 mm
(400 nominal 0.5 mm steps per case).  The complete CSV curves, summaries and
comparison plot are versioned under
`results/SPEAR/jeong_elnashai/sensitivity/concretecm_zero_tension/`.

| Metric | Fig. 2.8 | Production placeholder | Continuous envelope |
|---|---:|---:|---:|
| Peak shear (kN) | 354.363 | 349.132 | 352.955 |
| Peak error | — | -1.48% | -0.40% |
| Peak displacement (mm) | 74.194 | 55.000 | 56.500 |
| Curve MAE (kN) | — | 51.184 | 26.404 |
| Curve RMSE (kN) | — | 55.480 | 30.944 |
| Maximum absolute error (kN) | — | 90.384 | 56.911 |

The compression-envelope correction approximately halves the +X curve MAE and
removes much of the excessive post-peak degradation. It does not fix the early
peak displacement. The remaining discrepancy is therefore not admissibly
solved by compression-tail replacement alone.

| Case | Reference peak (kN) | Sensitivity peak (kN) | Peak error | Reference/model peak displacement (mm) | Curve MAE (kN) |
|---|---:|---:|---:|---:|---:|
| xp100 | 354.363 | 352.955 | -0.40% | 74.19 / 56.50 | 26.40 |
| xn100 | 367.335 | 359.942 | -2.01% | -82.58 / -56.50 | 27.13 |
| yp100 | 392.689 | 468.647 | +19.34% | 94.84 / 110.50 | 74.81 |
| yn100 | 454.009 | 496.827 | +9.43% | -147.74 / -78.50 | 51.27 |

The result is directionally inconsistent: the continuous zero-tension
envelope substantially improves both X curves but worsens both Y peak errors,
especially +Y.  It is therefore rejected as a production replacement.  This
also falsifies the hypothesis that the compression tail alone explains the
remaining four-direction discrepancy.

## Acceptance status

SPEAR-M0 remains **NOT VALIDATED**. Production `Concrete02` remains unchanged.
Acceptance still requires:

1. the numerical `ft` and tensile branch actually used for SPEAR `con2`;
2. a dimensioned or otherwise verifiable bent-bar transition;
3. quantitative mode-shape comparison, not periods alone.

No FVD, optimization, NLTHA/MSA or FEMA P-58 work is authorized.
