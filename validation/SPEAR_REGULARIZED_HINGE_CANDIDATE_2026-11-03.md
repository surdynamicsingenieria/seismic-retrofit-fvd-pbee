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

1. compare the recorded member mechanism with any recoverable published
   member-by-member hinge sequence, especially +Y;
2. resolve the failed admissible hinge-integration sensitivity gate;
3. retain the unrecovered ZEUS-NL `con2` and bent-bar coordinates as explicit
   epistemic limitations.

## Pointwise curve audit and hinge-integration sensitivity — 2026-11-04

The comparison utility now accepts explicit input and output directories, so
candidate curves can be audited without overwriting the production comparison.
For `HingeMidpoint`, the full common-range comparison gives:

| Case | Curve MAE (kN) | RMSE (kN) | 20 mm secant error | 40 mm secant error |
|---|---:|---:|---:|---:|
| +X | 42.10 | 45.80 | +22.63% | +19.14% |
| -X | 50.57 | 55.15 | +27.12% | +18.94% |
| +Y | 43.60 | 46.72 | +24.88% | +22.91% |
| -Y | 33.87 | 40.72 | +28.67% | +24.39% |

Thus the candidate matches peak strength substantially better than complete
curve shape: it is consistently too stiff over the first 20--40 mm, and its
peak occurs earlier than the digitized Fig. 2.8 peak in every direction. The
+Y peak-strength discrepancy remains +13.98%.

An independent quadrature sensitivity replaced only `HingeMidpoint` with
`HingeRadauTwo`, retaining the same Paulay--Priestley hinge lengths, sections,
materials, geometry, mass, gravity, load patterns and solver recovery sequence.

| Case | Reached displacement | Peak (kN) | Peak error | Fallback attempts |
|---|---:|---:|---:|---:|
| +X | +51.5 mm | 305.82 | -13.70% | 31 |
| -X | -48.5 mm | 312.29 | -14.99% | 31 |
| +Y | +103.5 mm | 368.38 | -6.19% | 33 |
| -Y | -80.0 mm | 394.23 | -13.17% | 56 |

All four `HingeRadauTwo` analyses exhausted adaptive recovery before the
nominal 200 mm target. Their pointwise errors are reported only over the
truncated common displacement range and must not be compared as if they were
complete curves. Pre-gravity periods remain close to `HingeMidpoint`
(0.49025, 0.42975, 0.36059 and 0.16962 s), confirming that the divergence is a
nonlinear integration sensitivity rather than an initial-stiffness change.

**Gate result: FAILED.** The nonlinear response is materially sensitive to an
admissible plastic-hinge quadrature. `HingeMidpoint` remains the numerically
robust candidate for continued diagnostics, but is not promoted to a final,
formulation-independent physical validation. Member-level curvature/plastic
rotation recording and a mechanism comparison are addressed in the following
section.

## Recorded deformation mechanism — 2026-11-04

The pushover driver now records peak storey drifts and, for regularized
force-based members, the maximum absolute rotational components returned by
OpenSees `plasticDeformation`. Complete member rankings are stored in the four
`*_mechanism.json` files.

| Case | Storey 1 drift | Storey 2 drift | Storey 3 drift | Governing member / plastic rotation |
|---|---:|---:|---:|---|
| +X | 5.864% | 0.615% | 0.352% | S1 C2 / 0.0706 rad |
| -X | 6.450% | 0.628% | 0.332% | S1 C1 / 0.0788 rad |
| +Y | 4.798% | 1.242% | 0.664% | S1 C4 / 0.0584 rad |
| -Y | 3.291% | 2.971% | 0.462% | S1 C4 / 0.0411 rad |

Both X cases and +Y form a pronounced first-storey column mechanism: all nine
first-storey columns occupy the first nine positions in the plastic-rotation
ranking. The -Y response spreads into the second storey and beam B10; this is
also the only direction whose first- and second-storey drifts are comparable.
Therefore the global softening is no longer inferred only from the roof curve:
it is traced directly to member and storey responses.

This closes the recorder implementation task, but not the physical mechanism
gate. MAE 04-03 does not provide a numerical member-by-member hinge sequence
against which these rotations can be accepted, and the failed quadrature
sensitivity remains. The earlier sentence requiring recorders is superseded by
this recorded audit; comparison to recoverable experimental/ZEUS-NL mechanism
data is still pending.

### Direct comparison with MAE 04-03 Figure 2.10

A renewed source check recovered the qualitative acceptance target immediately
following Fig. 2.8. MAE 04-03 states that, after peak in X, the first storey
becomes much weaker and top displacement is governed mainly by first-storey
drift. It also states that in Y the first- and second-storey drifts are close,
because C6 distributes damage and prevents a weak-storey mechanism.

The recorded candidate therefore has a mixed mechanism result:

- **+X and -X: consistent.** First-storey drift is about 9--19 times the upper
  storey drifts and all nine S1 columns lead the plastic-rotation ranking.
- **-Y: qualitatively consistent.** Storey 1 and 2 drifts are 3.291% and
  2.971%, and the mechanism extends into S2 columns and beam B10.
- **+Y: inconsistent.** Storey 1 drift is 4.798% versus 1.242% at storey 2,
  and all nine S1 columns lead the ranking. The model produces a first-storey
  concentration that the report says C6 should prevent in Y.

This source comparison identifies +Y as a physical mechanism error, not merely
a +13.98% peak-strength error. No parameter is changed to hide it. The leading
source-locked items to audit are C6 strong-axis section response, concrete
tension in C6 under +Y, and the exact beam reinforcement transition; the
unrecovered ZeusNL `con2` tensile input remains directly relevant.

The report also resolves an apparent contradiction in secondary literature:
with rigid links the pre-test analytical model develops the weak mechanism at
the first storey, while models without rigid links and significant fixed-end
rotation move it to the second storey (MAE 04-03, Sec. 7.2.2.3 and conclusions).
The present candidate includes rigid links, so a first-storey X mechanism is
the correct comparison target.

## Source-correct Section 2 floor model — 2026-11-05

The robust hinge candidate was rerun without rigid-diaphragm constraints.
This is not an optional calibration: MAE 04-03 Section 2.2 omits the slab and
Section 5.2 explicitly introduces a rigid diaphragm only in a later refined
model. Figure 2.8 is a result of the Section 2 model. Roof control and reported
storey drifts use C3, consistent with Figs. 2.10, 2.17 and 4.3.

| Case | Peak (kN) | Peak error | Curve MAE (kN) | 20 mm secant error | Reached |
|---|---:|---:|---:|---:|---:|
| +X | 328.07 | -7.42% | 21.62 | -9.74% | +200 mm |
| -X | 324.00 | -11.80% | 22.02 | -2.08% | -189 mm |
| +Y | 351.82 | -10.41% | 36.68 | -9.90% | +123.5 mm |
| -Y | 367.54 | -19.05% | 72.77 | -11.43% | -200 mm |

The +Y mechanism discrepancy is removed: peak recorded drifts are 1.645%,
1.608% and 0.927% in storeys 1--3. The first two are nearly equal, as required
by the report's description of C6 distributing damage in Y. In -Y the values
are 2.244%, 3.103% and 1.334%, still distributed rather than a basal mechanism.
Both X cases retain the expected first-storey concentration.

Initial periods remain close to the published modal state at 0.49038, 0.43323,
0.36199 and 0.17183 s. The excessive post-gravity period shift is retained as
evidence that nodal gravity application is not equivalent to the original
Fig. 2.6 beam loading state.

**Baseline decision:** the no-diaphragm formulation supersedes the earlier
rigid-diaphragm candidate for physical validation against Fig. 2.8. The code
default is changed accordingly. The earlier 21-pair robustness suite is not a
validation of this source-correct baseline and must not be used downstream.
Remaining strength underprediction cannot be corrected by restoring an
incompatible diaphragm; it remains tied to the unrecovered beam-gravity ledger,
ZeusNL material equivalence and hinge-integration sensitivity.

Production FVD/PBEE remains closed until these candidate-level checks finish.

## Technical sources

- Scott and Fenves (2006), *Plastic Hinge Integration Methods for Force-Based
  Beam-Column Elements*, ASCE JSE 132(2):244-252.
- OpenSees `HingeMidpoint` and beam-integration documentation.
- Paulay and Priestley plastic-hinge expression as reproduced in the technical
  literature and linked in the validation source ledger.
