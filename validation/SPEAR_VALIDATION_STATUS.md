# SPEAR VALIDATION STATUS

Date: 2026-10-14
Branch: `spear-jeong-elnashai-m0`

## Current state: FIBRE T-BEAM DIAGNOSTIC RUN; GRAVITY/MASS INPUTS PENDING

SPEAR-M0 is not physically validated and must not be used for FVD, optimization,
NLTHA/MSA or FEMA P-58.

## Actions completed in this pass

- Audited the Jeong-Elnashai pushover driver and identified an inadmissible
  automatic selection of the lateral pushover mode by effective modal mass.
- Removed that selection from the validation workflow. MAE 04-03 Section 2.3.1
  requires lateral force distribution proportional to first mode shape and mass
  distribution, followed by the Fig. 2.7 plan redistribution.
- Implemented the source-locked unidirectional cases `xp100`, `xn100`, `yp100`,
  `yn100` using Fig. 2.7 fractions.
- Digitized the supplied Fig. 2.8 image as a machine-readable reference curve.
- Ran diagnostic pushover in all four directions to +/-200 mm.
- Compared the diagnostic curves against the digitized Fig. 2.8 reference.
- Re-ran the executable modal model without stiffness or mass calibration.
- Source-locked the Fig. 2.3 reinforcement data in code and corrected the
  diagnostic column cover from 31 mm to the published 15 mm.
- Added the full digitized Fig. 2.8 CSV to the repository, so the comparison
  script no longer depends on an untracked local reference file.
- Extended the Fig. 2.8 comparison utility to emit an SVG plot.
- Wrote reproducible run outputs under `results/SPEAR/jeong_elnashai/`.
- Replaced the elastic beams with source-locked 250 x 500 mm fibre T-sections,
  individual published effective flange widths, and the Fig. 2.3 typical
  bent-bar layout using five Gauss-Lobatto integration points.
- Separated pre- and post-gravity eigenvalue states and source-locked the
  Eq. 2.5 pushover pattern to the pre-gravity mode used by ZeusNL eigenvalue
  analysis. All four cases now reach approximately +/-200 mm.

## Modal comparison

| Mode | MAE 04-03 target (s) | OpenSeesPy M0 (s) | Error |
|---:|---:|---:|---:|
| 1 | 0.510 | 0.543523 | +6.57% |
| 2 | 0.460 | 0.466114 | +1.33% |
| 3 | 0.400 | 0.356272 | -10.93% |
| 4 | 0.180 | 0.182575 | +1.43% |

## Pushover gate

Executed only as a diagnostic run, not an acceptance run.

The previous implementation selected a lateral mode automatically from modal
effective mass. That is not the MAE 04-03 procedure and can hide modeling errors
in an irregular torsionally coupled frame.

Source-locked pattern rule now used:

- Floor distribution: `Fi = V * phi_i * m_i / sum(phi_i * m_i)`, using the first
  mode shape as stated in MAE 04-03 Eq. 2.5.
- X plan redistribution from Fig. 2.7: `0.24 Vx`, `0.50 Vx`, `0.26 Vx`.
- Y plan redistribution from Fig. 2.7: `0.15 Vy`, `0.44 Vy`, `0.41 Vy`.

Required implementation work before running nonlinear acceptance pushover:

- Exact Fig. 2.6 nodal gravity and seismic mass allocation at beam-column
  connections.
- Recover the concrete tensile strength used in the original SPEAR ZeusNL
  `con2` material definition.

## Diagnostic pushover comparison

The fibre T-beam diagnostic remains too strong in all four directions. The
correct pre-gravity first mode removes the previous `yn100` convergence stop,
but does not close the physical capacity discrepancy.

| Case | Fig. 2.8 Vmax (kN) | Diagnostic Vmax (kN) | Peak error |
|---|---:|---:|---:|
| `xp100` | 354.363 | 515.432 | +45.45% |
| `xn100` | 367.335 | 510.330 | +38.93% |
| `yp100` | 392.689 | 640.686 | +63.15% |
| `yn100` | 454.009 | 649.376 | +43.03% |

The current fibre model periods are 0.57437, 0.50643, 0.37823 and 0.18678 s.
Their deviation from both the published periods and the separate elastic modal
baseline shows that nonlinear section initial stiffness/material assumptions
must be audited together with the unresolved nodal mass ledger; they are not
to be calibrated.

## Fibre modal-state audit

The discrepancy was separated into initial-section and gravity-state effects:

| Mode | Published (s) | Elastic baseline (s) | Fibre pre-gravity (s) | Fibre post-gravity (s) |
|---:|---:|---:|---:|---:|
| 1 | 0.510 | 0.543523 | 0.511168 | 0.574370 |
| 2 | 0.460 | 0.466114 | 0.443895 | 0.506429 |
| 3 | 0.400 | 0.356272 | 0.341330 | 0.378234 |
| 4 | 0.180 | 0.182575 | 0.171646 | 0.186778 |

Gravity increases the fibre-model periods by 12.36%, 14.09%, 10.81% and
8.82%, respectively. This is not solver noise. The current `Concrete02`
definition has zero tensile strength and its compression-envelope initial
tangent is 25 GPa, while the elastic beams use 23.5 GPa. Reinforcing steel is
also present in the nonlinear fibre sections but not in the concrete-only
column sections of the modal baseline. Therefore the two implementations are
not stiffness-equivalent.

MAE 04-03 specifies a modified Mander model, concrete strength of 25 MPa and a
confinement factor of 1.01, but does not state the numerical concrete tensile
strength in Section 2.2.3. The ZeusNL manual confirms that the `con2` model
requires `fc`, `ft`, crushing strain and confinement factor and lists 2.2 MPa
only as a typical example for 20 MPa concrete. It is not evidence that SPEAR
used 2.2 MPa. The current zero-tension `Concrete02` mapping is therefore not
source-locked and must not be adjusted merely to force a period match.

## Mass-source audit

The current floor tuples (65.5, 65.5 and 64.1 t; centers 4.53/5.29 and
4.57/5.33 m; polar masses 1254, 1254 and 1196 tm2) were traced to the
Stratan-Fajfar SPEAR assessment. They are not a recovered Jeong-Elnashai
ZeusNL nodal mass ledger. Their total is 195.1 t, corresponding to 1913.35 kN
with the report's 9.807 m/s2 gravity, whereas MAE 04-03 states a total building
weight of 1957 kN (199.55 t). The discrepancy is -2.23%.

Consequently, all modal and pushover results using these tuples remain
diagnostic. Substituting a different published partner-model mass set would mix
model assumptions and is prohibited.

## Required gates

- [x] Executable 3D modal model
- [x] Modal periods computed against MAE 04-03 targets
- [ ] Mode-shape comparison documented quantitatively
- [x] Fibre periods separated into pre- and post-gravity states
- [ ] Source-locked gravity and nodal mass allocation
- [x] Source-locked member reinforcement data from Fig. 2.3
- [x] Diagnostic fibre implementation of the Fig. 2.3 bent-bar beam layout
- [x] Published lateral pushover patterns implemented
- [x] Diagnostic pushover +X (`xp100`)
- [x] Diagnostic pushover -X (`xn100`)
- [x] Diagnostic pushover +Y (`yp100`)
- [x] Diagnostic pushover -Y (`yn100`) to full target
- [x] Fig. 2.8 reference curve digitized
- [x] Quantitative Fig. 2.8 curve comparison against diagnostic OpenSees results
- [ ] Acceptance pushover with source-locked reinforcement and Fig. 2.6 mass/loading

## Reproducibility note

In this runtime, OpenSeesPy 3.8.0.0 requires:

```bash
MPICH_INTERFACE_HOSTNAME=127.0.0.1 python models/SPEAR/jeong_elnashai/spear_m0_jeong_elnashai.py
MPICH_INTERFACE_HOSTNAME=127.0.0.1 python models/SPEAR/jeong_elnashai/spear_m0_jeong_elnashai_nonlinear.py
python validation/compare_pushover_to_fig_2_8.py
```

Without that environment variable, MPI initialization fails before model
construction.


## Spatial Fig. 2.7 correction and global mass closure — 2026-10-17

The pushover implementation previously computed the three Fig. 2.7 frame
fractions but summed them and applied the resultant at the floor centre of
mass. That preserved storey shear but removed the published torsional moment.
Loads are now applied at the three perimeter frame points shown in Fig. 2.7.

Updated diagnostic results are:

| Case | Fig. 2.8 peak (kN) | OpenSees peak (kN) | Peak error | Reached displacement |
|---|---:|---:|---:|---:|
| `xp100` | 354.363 | 516.040 | +45.62% | +199.88 mm |
| `xn100` | 367.335 | 511.259 | +39.18% | -200.12 mm |
| `yp100` | 392.689 | 635.683 | +61.88% | +200.17 mm |
| `yn100` | 454.009 | 510.692* | +12.48%* | -52.83 mm |

The `yn100` result is truncated after a documented convergence failure and is
not an acceptance peak comparison. The return of this directional stop after
restoring the spatial load torque confirms that collapsing Fig. 2.7 to a CM
force was physically consequential.

The global Fig. 2.6 gravity/mass reconstruction now closes without calibration:
`1955.856 kN` reconstructed versus `1957.000 kN` published, a residual of
`-1.144 kN (-0.0585%)`. The balance uses the full 9.70 x 10.50 m slab plan,
including cantilever strips outside the framing axes, the Table 2.1 clear beam
spans and full 3.0 m column storey heights. The exact nearest-beam node ledger
remains pending; global mass is no longer the unresolved part of that blocker.


## Table 3.1 nodal mass recovery — 2026-10-17

The Fig. 2.6 node-by-node ledger was recovered from the gravity axial forces in
Table 3.1: floor load at each column is the difference between axial forces
below and above the floor, with the third-storey force used at the roof. This
produces floor weights of 659.63, 659.66 and 615.95 kN, or masses of 67.261,
67.264 and 62.807 t. The 1935.24 kN total agrees with the independent workshop
mass set and exposes an internal 21.76 kN (1.11%) inconsistency with the
report's isolated 1957 kN scalar.

The model now places translational mass at all nine beam-column connections and
no longer imports Stratan-Fajfar floor polar inertias. Gravity loads use the
same recovered nodal ledger. With the source-required 2.50 m deformable column
heights, elastic periods are 0.51446, 0.44775, 0.37304 and 0.17797 s (errors
+0.87%, -2.66%, -6.74% and -1.13%).

Updated nonlinear peaks are 544.24, 577.60, 661.28 and 681.03 kN for xp, xn,
yp and yn. The yn analysis reaches -158.56 mm before its documented stop.
Capacity remains 50-68% above Fig. 2.8. Consequently mass provenance is closed
as a principal cause; the active blockers are the unrecovered ZeusNL `con2`
tensile input, exact bent-bar transition representation and section-level
moment-curvature verification.


## Column bar-centroid audit — 2026-10-18

Column longitudinal bars were corrected from a 15 mm centroid offset to the
published-detail centroid distance `15 + 8 + 6 = 29 mm` (clear cover, Phi8
stirrup and half Phi12). This source-required correction reduces diagnostic
peaks to 513.98, 543.62, 633.65 and 651.79 kN for xp, xn, yp and yn. Peak
errors remain +45.04%, +47.99%, +61.36% and +43.56%; yn is truncated at
-166.05 mm.

Pre-gravity fibre periods are now 0.49008, 0.42951, 0.36042 and 0.16958 s;
post-gravity values are 0.54397, 0.48694, 0.40130 and 0.18279 s. The detailing
correction improves capacity but does not validate the model. C6 Table 3.1
curvature values remain inconsistent with a direct strong-axis interpretation
of the published 750 x 250 mm section and are retained as an explicit source
blocker rather than forcing an axis convention.
