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
| `xp100` | 354.363 | 516.040 | +45.62% | 145.199 |
| `xn100` | 367.335 | 511.259 | +39.18% | 124.168 |
| `yp100` | 392.689 | 635.683 | +61.88% | 200.343 |
| `yn100` | 454.009 | 510.692* | +12.48%* | 82.838* |

The 2026-10-17 audit found that the code computed the Fig. 2.7 three-frame
fractions but summed each row and applied the resultant at the floor centre of
mass.  That preserved storey shear but discarded the prescribed torsional
moment.  The loads are now applied at the three perimeter frame points shown in
Fig. 2.7.  Cases `xp100`, `xn100` and `yp100` reach approximately 200 mm.
`yn100` now stops at -52.83 mm after one documented fallback attempt; values
marked with an asterisk are therefore truncated diagnostics, not peak-capacity
acceptance comparisons.  This directional failure is evidence that the Fig.
2.7 torque is structurally active and must not be collapsed to a CM force.

## Fig. 2.6 global mass balance

A source-only reconstruction from Fig. 2.2, Table 2.1 and Sec. 2.2.4 gives:

| Component | Weight (kN) |
|---|---:|
| Three 9.70 x 10.50 x 0.15 m slabs + 0.5 kN/m2 finish + 0.6 kN/m2 live load | 1459.826 |
| Beam drops below the slab, using the 53.5 m sum of published clear spans | 344.325 |
| Three storeys of columns using the 3.0 m centreline height | 151.705 |
| **Reconstructed total** | **1955.856** |
| **MAE 04-03 total** | **1957.000** |

The residual is -1.144 kN (-0.0585%), consistent with published-dimension
rounding and without fitted input.  This closes the global mass reconstruction
and shows that the full rectangular slab, including cantilever strips outside
the framing axes, is required.  The node-by-node nearest-beam allocation is
still pending and remains an acceptance gate.

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

## Table 3.1 nodal-ledger reconstruction - 2026-10-17

The exact nodal gravity pattern was recovered from the published column axial
forces.  At floors 1 and 2, the load entering each column is the difference
between axial force below and above the floor; at the roof it is the third
storey axial force.  The derived floor weights are 659.63, 659.66 and 615.95
kN (67.261, 67.264 and 62.807 t).  Their 1935.24 kN total independently agrees
with the workshop mass set, exposing an internal 21.76 kN (1.11%) discrepancy
with the isolated 1957 kN scalar in MAE 04-03.

Masses are now assigned to the nine beam-column connections, as required by
Sec. 2.2.4, with no assumed floor polar inertia.  With the source-required
2.50 m deformable column heights, the elastic periods become 0.51446, 0.44775,
0.37304 and 0.17797 s: errors +0.87%, -2.66%, -6.74% and -1.13%.

The corresponding nonlinear pre-gravity periods are 0.48449, 0.42564, 0.35732
and 0.16750 s, while post-gravity periods are 0.53820, 0.48315, 0.39821 and
0.18052 s.  The post-gravity values are very close to the published third and
fourth periods, but the report/manual evidence still indicates that the
published eigenproblem is pre-gravity.  This contrast reinforces the remaining
need to recover the ZeusNL `con2` tensile input rather than selecting a modal
state merely because it fits.

Updated source-ledger diagnostic peaks are 544.24, 577.60, 661.28 and 681.03
kN for xp, xn, yp and yn.  The first three reach 200 mm; yn stops at -158.56
mm.  Capacity remains 50-68% above Fig. 2.8, so mass provenance is no longer a
credible explanation for the strength discrepancy.

## Column bar-centroid correction - 2026-10-18

The earlier column fibres interpreted the published 15 mm concrete cover as a
bar-centroid distance.  Fig. 2.3 also specifies Phi8 stirrups and Phi12
longitudinal bars, so the source-consistent centroid distance is
`15 + 8 + 12/2 = 29 mm`.  Section equilibrium checks against Table 3.1 show
that 29 mm produces materially closer regular-column yield curvatures than
15 mm.  This is a detailing correction, not a capacity calibration.

After correction, pre-gravity fibre periods are 0.49008, 0.42951, 0.36042 and
0.16958 s; post-gravity periods are 0.54397, 0.48694, 0.40130 and 0.18279 s.
Diagnostic peaks decrease to 513.98, 543.62, 633.65 and 651.79 kN.  Errors
against Fig. 2.8 remain +45.04%, +47.99%, +61.36% and +43.56%; yn stops at
-166.05 mm.  The correction is physically required but does not close the
capacity discrepancy.

The C6 entries in Table 3.1 remain anomalous under a direct strong-axis
interpretation of the published 750 x 250 mm section: their listed yield
curvatures are of the same order as the weak-axis/regular-column values.  No
axis reinterpretation is applied until this is resolved from a primary source
or a verified ZeusNL section convention.
