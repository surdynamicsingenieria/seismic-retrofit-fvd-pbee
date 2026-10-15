# SPEAR-M0 nonlinear capacity audit - 2026-10-14

Branch: `spear-jeong-elnashai-m0`

## Source findings

MAE 04-03 Fig. 2.3 gives the member reinforcement used by the pre-test model:

| Item | Published detail | Repository status |
|---|---|---|
| Beam section | 250 x 500 mm T-beam, 150 mm slab | geometry/source locked |
| Typical beam longitudinal steel | 2Phi12 top at section A-A', 4Phi12 bottom at section A-A', 2Phi12 bent up at beam ends | diagnostic fibre implementation complete |
| Beam transverse steel | Phi8/0.20 m | source data locked |
| Regular columns C1-C5, C7-C9 | 250 x 250 mm, 4Phi12, Phi8/0.25 m stirrups | source data locked and represented in diagnostic columns |
| Column C6 | 750 x 250 mm, 10Phi12, Phi8/0.25 m stirrups | source data locked and represented in diagnostic column |
| Cover | 15 mm for all members | corrected in diagnostic column fibre sections |

MAE 04-03 Sec. 2.2.4 states that gravity load is DL+0.3LL, slab loads are distributed to nearest beams per Fig. 2.6, and seismic masses are placed at beam-column connections. The current executable nonlinear diagnostic still uses one rigid-diaphragm master mass per floor and uniform floor gravity reactions. That is not acceptable for final validation.

## Fibre T-beam diagnostic

The beam implementation uses the individual Fig. 2.2 effective flange widths,
the 150 mm slab, a 250 x 500 mm web/depth, 15 mm clear cover, Phi8 stirrups and
Phi12 longitudinal bars. Five Gauss-Lobatto points are used: the two endpoint
sections contain 4 top and 2 bottom bars, while the three interior sections use
the A-A' arrangement of 2 top and 4 bottom bars. Fig. 2.3 does not dimension the
bend transition, so this remains an explicit diagnostic discretization rather
than an acceptance-level reconstruction.

| Case | Fig. 2.8 Vmax (kN) | Diagnostic Vmax (kN) | Peak error | MAE (kN) |
|---|---:|---:|---:|---:|
| `xp100` | 354.363 | 515.432 | +45.45% | 144.880 |
| `xn100` | 367.335 | 510.330 | +38.93% | 123.436 |
| `yp100` | 392.689 | 640.686 | +63.15% | 203.639 |
| `yn100` | 454.009 | 649.376 | +43.03% | 145.043 |

All four analyses reached approximately +/-200 mm. The prior `yn100` stop was
removed by using the source-consistent pre-gravity first mode for Eq. 2.5,
rather than a mode recomputed after the gravity analysis.

## Blocking items before acceptance

1. Convert Fig. 2.6 gravity distribution into nodal loads and seismic masses at beam-column connections.
2. Recompute floor mass, center of mass, and polar mass moment from the nodal ledger before modal acceptance.
3. Audit published concrete constitutive inputs and the exact bent-bar transition detail; do not tune them.
4. Re-run the four pushover cases and Fig. 2.8 comparison after the material and mass ledgers are source-locked.

## Additional material-model blocker

The modal-state audit demonstrates that gravity changes the four fibre-model
periods by +12.36%, +14.09%, +10.81% and +8.82%. MAE 04-03 describes the
concrete law as a modified Mander model defined in part by tensile strength,
but Section 2.2.3 supplies no numerical tensile-strength value. The present
OpenSees `Concrete02` mapping uses `ft=0`, which is not source-locked and causes
immediate loss of tensile tangent stiffness under gravity. This input must be
recovered from a primary SPEAR/ZeusNL source or retained as an explicit blocker;
it must not be calibrated from Fig. 2.8.

No FVD, optimization, NLTHA/MSA, or FEMA P-58 work is permitted until those gates pass.
