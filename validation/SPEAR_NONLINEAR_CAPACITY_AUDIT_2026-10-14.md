# SPEAR-M0 nonlinear capacity audit - 2026-10-14

Branch: `spear-jeong-elnashai-m0`

## Source findings

MAE 04-03 Fig. 2.3 gives the member reinforcement used by the pre-test model:

| Item | Published detail | Repository status |
|---|---|---|
| Beam section | 250 x 500 mm T-beam, 150 mm slab | geometry/source locked |
| Typical beam longitudinal steel | 2Phi12 top at section A-A', 4Phi12 bottom at section A-A', 2Phi12 bent up at beam ends | source data locked; fibre implementation pending |
| Beam transverse steel | Phi8/0.20 m | source data locked |
| Regular columns C1-C5, C7-C9 | 250 x 250 mm, 4Phi12, Phi8/0.25 m stirrups | source data locked and represented in diagnostic columns |
| Column C6 | 750 x 250 mm, 10Phi12, Phi8/0.25 m stirrups | source data locked and represented in diagnostic column |
| Cover | 15 mm for all members | corrected in diagnostic column fibre sections |

MAE 04-03 Sec. 2.2.4 states that gravity load is DL+0.3LL, slab loads are distributed to nearest beams per Fig. 2.6, and seismic masses are placed at beam-column connections. The current executable nonlinear diagnostic still uses one rigid-diaphragm master mass per floor and uniform floor gravity reactions. That is not acceptable for final validation.

## Diagnostic result after source-lock correction

The four pushover analyses completed to +/-200 mm with no convergence fallback. Because beams are still elastic and the gravity/mass allocation remains simplified, these are diagnostic runs only.

| Case | Fig. 2.8 Vmax (kN) | Diagnostic Vmax (kN) | Peak error | MAE (kN) |
|---|---:|---:|---:|---:|
| `xp100` | 354.363 | 518.273 | +46.25% | 148.760 |
| `xn100` | 367.335 | 514.301 | +40.01% | 128.940 |
| `yp100` | 392.689 | 703.743 | +79.21% | 201.551 |
| `yn100` | 454.009 | 746.955 | +64.52% | 147.821 |

The correction to the published 15 mm cover increased capacity relative to the prior 31 mm diagnostic model. This reinforces that the remaining mismatch cannot be solved by lateral pattern selection and must be addressed by source-locked nonlinear member modelling and mass/load allocation.

## Blocking items before acceptance

1. Replace elastic beams with fibre T-sections that represent the Fig. 2.3 bent-bar layout without inventing member-specific variants.
2. Convert Fig. 2.6 gravity distribution into nodal loads and seismic masses at beam-column connections.
3. Recompute floor mass, center of mass, and polar mass moment from the nodal ledger before modal acceptance.
4. Re-run modal periods, mode shapes, four pushover cases, and quantitative Fig. 2.8 comparison.

No FVD, optimization, NLTHA/MSA, or FEMA P-58 work is permitted until those gates pass.
