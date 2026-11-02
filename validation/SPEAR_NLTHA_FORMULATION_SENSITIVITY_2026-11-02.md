# SPEAR-M0 NLTHA formulation sensitivity — 2026-11-02

## Scope

This controlled diagnostic follows the low-drift convergence audit of RSN 900
and 1633. It changes one numerical formulation choice at a time and retains the
same geometry, sections, materials, masses, gravity loads, damping, records and
unscaled amplitudes. A variant is not accepted merely because it converges.

The source-ledger baseline remains displacement-based subelements with
two-point Legendre integration and P-Delta column transformations. MAE 04-03
states second-order Gaussian quadrature for the four subelements; therefore the
four-point variants below are diagnostics, not replacements for the baseline.

## Directional results

| Case | Variant | Last step | Requested | Max CM drift | Result |
|---|---|---:|---:|---:|---|
| RSN 900 X | baseline, 2-point | 825 | 2199 | 1.180% | incomplete |
| RSN 900 X | no P-Delta | 825 | 2199 | 1.008% | incomplete |
| RSN 900 X | force-based columns, 2-point | 825 | 2199 | 1.173% | incomplete |
| RSN 900 X | displacement-based columns, 4-point | 2199 | 2199 | 3.415% | complete |
| RSN 1633 X | baseline, 2-point | 598 | 2675 | 1.287% | incomplete |
| RSN 1633 X | no P-Delta | 598 | 2675 | 1.311% | incomplete |
| RSN 1633 X | force-based columns, 2-point | 600 | 2675 | 1.485% | incomplete |
| RSN 1633 X | displacement-based columns, 4-point | 2675 | 2675 | 2.078% | complete |
| RSN 1633 Y | baseline, 2-point | 533 | 2299 | 1.193% | incomplete |
| RSN 1633 Y | no P-Delta | 538 | 2299 | 1.871% | incomplete |
| RSN 1633 Y | force-based columns, 2-point | 534 | 2299 | 1.274% | incomplete |
| RSN 1633 Y | 4-point columns, 2-point beams | 539 | 2299 | 1.709% | incomplete |
| RSN 1633 Y | 2-point columns, 4-point beams | 533 | 2299 | 1.286% | incomplete |
| RSN 1633 Y | 4-point columns and beams | 541 | 2299 | 1.729% | incomplete |

Removing P-Delta and changing only the column element to force-based resolve
none of the three failures. Four-point column integration lets RSN 900-X and
RSN 1633-X finish, but RSN 1633-Y still stops within eight record intervals of
the baseline stop for every tested column/beam combination. This is evidence
of formulation sensitivity, not evidence that four-point integration is the
physically correct model.

## Modal invariance check

| Integration (columns/beams) | T1 pre (s) | T2 pre (s) | T3 pre (s) | T4 pre (s) |
|---|---:|---:|---:|---:|
| 2 / 2 | 0.490348 | 0.429894 | 0.360692 | 0.169641 |
| 4 / 2 | 0.490348 | 0.429894 | 0.360692 | 0.169641 |
| 2 / 4 | 0.490348 | 0.429894 | 0.360692 | 0.169641 |
| 4 / 4 | 0.490348 | 0.429894 | 0.360692 | 0.169641 |
| 6 / 6 | 0.490348 | 0.429894 | 0.360692 | 0.169641 |

The largest pre-gravity period spread is below 1e-8 s. Post-gravity periods
also differ by less than 0.04% across the tested variants. Thus integration
order does not explain the modal mismatch, although it materially changes the
nonlinear path and convergence of two records.

## Decision

No tested formulation passes the NLTHA objectivity gate. The baseline remains
unchanged. Production NLTHA, FVD, fragility and PBEE remain blocked. The next
source-led checks are the concrete tension/unloading mapping and member
localization regularization/mesh objectivity; neither may be calibrated to the
record outcomes.

Machine-readable JSON summaries and execution logs are stored in
`results/SPEAR/nltha/peer_partial_21/formulation_sensitivity/`. Full histories
are reproducible local artifacts excluded from Git.
