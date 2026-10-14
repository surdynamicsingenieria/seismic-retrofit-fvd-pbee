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
| `xp100` | 354.363 | 515.176 | +45.38% | 144.574 |
| `xn100` | 367.335 | 509.977 | +38.83% | 123.112 |
| `yp100` | 392.689 | 639.248 | +62.79% | 202.797 |
| `yn100` | 454.009 | 509.052* | +12.12%* | 81.570* |

`yn100` is incomplete: convergence stopped at -53.33 mm versus the -200 mm
target and the reference peak occurs at -147.74 mm. Its error values cover only
the available common range and must not be interpreted as validation.

## Blocking items before acceptance

1. Convert Fig. 2.6 gravity distribution into nodal loads and seismic masses at beam-column connections.
2. Recompute floor mass, center of mass, and polar mass moment from the nodal ledger before modal acceptance.
3. Audit published concrete constitutive inputs and the exact bent-bar transition detail; do not tune them.
4. Resolve the `yn100` compatibility failure and re-run the four pushover cases and Fig. 2.8 comparison.

No FVD, optimization, NLTHA/MSA, or FEMA P-58 work is permitted until those gates pass.
