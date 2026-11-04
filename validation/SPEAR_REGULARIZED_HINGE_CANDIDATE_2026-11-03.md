# SPEAR-M0 regularized hinge candidate — 2026-11-03

## Purpose

The distributed local fibre model failed the spatial-objectivity gate. This
candidate replaces the four displacement-based subelements per member with one
force-based member using `HingeMidpoint` integration. The existing source-led
fibre sections are retained at both ends and the existing middle section is
used in the member interior. Geometry, rigid offsets, masses, gravity loads,
materials, P-Delta transformations, damping and records are unchanged.

No parameter was selected from Fig. 2.8 or from NLTHA convergence. The physical
hinge length is calculated independently as

`Lp = 0.08 L + 0.022 fy db`

using the deformable member length, the published SPEAR `fy=458.67 MPa`, and
the 12 mm longitudinal bar represented in the fibre sections. This expression
is attributed to Paulay and Priestley and includes flexural spread and bar-slip
contributions. OpenSees plastic-hinge integration confines yielding to a
specified length and was developed to overcome non-objective softening response
in force-based elements.

## Modal control

| Mode | Distributed pre-gravity (s) | Regularized pre-gravity (s) | Difference |
|---:|---:|---:|---:|
| 1 | 0.490348 | 0.489340 | -0.205% |
| 2 | 0.429894 | 0.429037 | -0.200% |
| 3 | 0.360692 | 0.360033 | -0.183% |
| 4 | 0.169641 | 0.169296 | -0.204% |

The candidate preserves the initial modal state without stiffness fitting.

## Four-direction pushover

| Case | Fig. 2.8 peak (kN) | Candidate peak (kN) | Peak error | Reached displacement |
|---|---:|---:|---:|---:|
| +X | 354.363 | 346.295 | -2.28% | +200 mm |
| -X | 367.335 | 353.410 | -3.79% | -200 mm |
| +Y | 392.689 | 447.602 | +13.98% | +197 mm |
| -Y | 454.009 | 469.936 | +3.51% | -200 mm |

Three directions are within 4% in peak strength. The +Y discrepancy remains
material and is not calibrated away. The +Y analysis stops 3 mm short of the
nominal target after adaptive increments; it nevertheless passes well beyond
the published peak displacement.

## Critical directional NLTHA

| Case | Distributed result | Regularized result | Peak drift | Peak roof displacement | Solver fallbacks |
|---|---|---|---:|---:|---:|
| RSN 900 X | incomplete 825/2199 | complete 2199/2199 | 3.232% | 114.2 mm | 0 |
| RSN 1633 X | incomplete 598/2675 | complete 2675/2675 | 2.020% | 90.3 mm | 0 |
| RSN 1633 Y | incomplete 533/2299 | complete 2299/2299 | 1.714% | 100.4 mm | 0 |

All three records that exposed low-drift localization now complete without a
single algorithm fallback or time-step subdivision. This strongly supports the
diagnosis that the previous failures were numerical localization rather than
physical collapse.

## Status and remaining gates

This formulation is promoted to **REGULARIZED CANDIDATE**, not final physical
validation. It satisfies initial modal preservation, four-direction global
capacity reasonableness and the three-record robustness check.

## Full provisional 21-pair bidirectional suite

The complete available FEMA-P695 subset was run with both horizontal
components applied simultaneously, 5% Rayleigh damping and no record scaling.
Eighteen of 21 pairs (85.7%) completed every requested step. All 18 complete
cases used the primary Newton algorithm with zero fallback attempts; their
largest storey drift was 3.773%.

| Pair | Completed steps | Time fraction | Last-state maximum drift | Classification |
|---|---:|---:|---:|---|
| RSN953 | 1487/2998 | 49.60% | 69.47% | instability-compatible nonconvergence |
| RSN1244 | 11391/17999 | 63.29% | 70.55% | instability-compatible nonconvergence |
| RSN1602 | 1953/5589 | 34.94% | 67.65% | instability-compatible nonconvergence |

The three incomplete histories are categorically different from the previous
distributed-fibre failures at low drift: each reached approximately 68--71%
storey drift before exhausting Newton, Krylov-Newton and line-search recovery.
These are last-converged-state diagnostics, not proof or calibrated estimates
of collapse capacity. No incomplete record is promoted as a final EDP.

The machine-readable suite summary, per-record summaries, logs and EDP table
are under
`results/SPEAR/nltha/peer_partial_21/regularized_hinge_midpoint_bidirectional/`.

Remaining work:

1. compare complete pushover curve shape and mechanism, especially +Y;
2. verify that response is insensitive to admissible hinge-integration choice;
3. retain the unrecovered ZEUS-NL `con2` and bent-bar coordinates as explicit
   epistemic limitations.

Production FVD/PBEE remains closed until these candidate-level checks finish.

## Technical sources

- Scott and Fenves (2006), *Plastic Hinge Integration Methods for Force-Based
  Beam-Column Elements*, ASCE JSE 132(2):244-252.
- OpenSees `HingeMidpoint` and beam-integration documentation.
- Paulay and Priestley plastic-hinge expression as reproduced in the technical
  literature and linked in the validation source ledger.
