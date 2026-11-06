# SPEAR VALIDATION STATUS

Date: 2026-10-30
Branch: `spear-jeong-elnashai-m0`

## Current state: ENGINEERING BENCHMARK ACCEPTED

SPEAR-M0 is accepted for the engineering fidelity required by this FVD/PBEE
research. Exact pointwise reproduction of Fig. 2.8 and recovery of the original
UIUC ZeusNL deck are not claimed. FVD development and baseline NLTHA are now
authorized; later optimization, MSA and FEMA P-58 retain separate gates.

The governing decision and numerical criteria are documented in
`validation/SPEAR_M0_ENGINEERING_ACCEPTANCE.md`. Historical diagnostic sections
below are retained as an audit trail and do not override this current status.

## Bidirectional NLTHA infrastructure — 2026-10-30

The engineering-accepted M0 baseline now has a simultaneous X-Y nonlinear
response-history driver. It accepts only manifest-defined pairs containing
exactly one X and one Y component, validates file SHA-256 values before model
construction, cross-checks PEER AT2 `NPTS` and `DT` headers, and rejects
component time-step mismatches. If paired components have unequal durations,
the shorter one is zero-padded only after its original samples and the exact
padding count is recorded in the output JSON.

A solver-independent constant-average-acceleration Newmark implementation now
computes linear pseudo-acceleration spectra. Its unit/formulation test uses an
analytic long-duration resonant harmonic input; it is not structural evidence.

The simultaneous synthetic 0.05 g X-Y smoke analysis completed 20/20 steps
without solver fallbacks. Peak roof displacements were 6.013 mm in X and
7.176 mm in Y; maximum storey drift ratios were 0.0841% in X and 0.0932% in Y;
base shears were 87.39 and 108.47 kN. These values verify execution and EDP
extraction only and are prohibited from physical interpretation.

An authenticated PEER NGA-West2 search was completed on 2026-10-30. Search
11648 explicitly submitted all 22 FEMA P-695 RSNs and requested 22 records, but
PEER returned 21 metadata rows and 21 record pairs. RSN 829 (Cape Mendocino,
Rio Dell Overpass) is the sole missing pair. PEER Report 2007/08 Table A.1
confirms the historical filenames `CAPEMEND/RI0270.at2` and
`CAPEMEND/RI0360.at2`. A separate station
search for Rio Dell Overpass did not recover it. This is now a precisely
identified external-data blocker, not a generic acquisition task. The 22-pair
identity ledger is committed at
`models/SPEAR/fvd/fema_p695_far_field_suite.csv`; no substitute waveform is
admitted. The PEER trace-package request passed both database notices, but no
ZIP was delivered to the browser download area, so the 21 available pairs have
not yet been admitted to the executable manifest. Site-specific hazard
definition remains a later, separate PBEE gate.

On 2026-11-01 the researcher supplied PEER package
`UnscaledAccRecord11683.zip`. Its archive integrity test passed. The package
contains 21 FEMA pairs and 42 horizontal AT2 traces; RSN 829 remains the only
missing pair. All 42 traces passed strict header/sample-count, finite-value,
unit, SHA-256 and within-pair time-step validation. Their time steps range from
0.0039 to 0.0200 s and sample counts from 1,999 to 18,000. The resulting
manifest is `models/SPEAR/fvd/manifests/fema_p695_peer_partial_21.json`.
Waveform bytes are retained only as licensed local inputs and are ignored by
Git; no NLTHA result from this partial suite may be represented as the complete
22-pair FEMA ensemble.

## Provisional unscaled partial-21 NLTHA — 2026-11-02

With explicit authorization to proceed without RSN 829, all 21 available pairs
were analyzed simultaneously in X and Y at their unscaled, as-recorded
intensity. Five-percent Rayleigh damping was anchored to pre-gravity modes 1
and 3. No record or material parameter was calibrated.

Thirteen cases completed every requested step. Eight stopped after Newton,
Krylov-Newton, Newton line search and deterministic adaptive subdivision down
to 1/16 of the record interval. The last-converged-state diagnostic separates:

- 2 instability-compatible cases with maximum drift >=10%: RSN 752 and 960;
- 4 severe-response cases with drift 2--10%: RSN 953, 1158, 1244 and 1602;
- 2 cases below 2% requiring numerical/model audit: RSN 900 and 1633.

This classification is not a formal collapse assessment. EDPs from incomplete
analyses are truncated histories and must not be used as final peaks. Compact
results, individual logs and JSON summaries are under
`results/SPEAR/nltha/peer_partial_21/`; full CSV histories remain reproducible
local artifacts excluded from Git.

Directional and element-level audit of the two sub-2% failures is documented
in `validation/SPEAR_NLTHA_CONVERGENCE_AUDIT_2026-11-02.md`. RSN 900 fails only
in X; RSN 1633 fails independently in X and Y. `EnergyIncr` reproduces the same
stopping steps as `NormDispIncr`. Last-state section scans expose extreme local
deformation (up to 24.086 1/m curvature and -1.055 axial strain in the C4
first-storey base segment for RSN 900-X) despite modest CM drift. This is a
model/formulation pathology, not evidence of a valid moderate response.

**Gate correction:** production NLTHA, FVD comparison, fragility and PBEE are
blocked pending mesh/element/material objectivity checks. The earlier
engineering acceptance remains applicable to the modal and pushover benchmark;
it does not establish NLTHA robustness.

## NLTHA formulation sensitivity — 2026-11-02

Controlled tests of P-Delta removal, force-based columns and two/four-point
column/beam integration are documented in
`validation/SPEAR_NLTHA_FORMULATION_SENSITIVITY_2026-11-02.md`. Removing
P-Delta and using force-based columns resolved none of the low-drift failures.
Four-point column integration completed RSN 900-X and RSN 1633-X, but every
tested formulation still stopped for RSN 1633-Y at essentially the same part
of the record. This is formulation sensitivity, not a validated correction.

Modal periods are invariant to the tested integration orders: the largest
pre-gravity spread across 2/2, 4/2, 2/4, 4/4 and 6/6 column/beam integration is
below 1e-8 s; post-gravity spreads are below 0.04%. The baseline remains the
source-led two-point formulation and the production NLTHA/FVD/PBEE gate stays
closed pending source-backed material and mesh-objectivity work.

## NLTHA mesh-objectivity audit — 2026-11-02

Every published 0.15L/0.35L/0.35L/0.15L subelement was split in half without
changing sections, materials or integration order. Elastic periods changed by
less than 0.0004%, but all three low-drift records failed earlier: RSN 900-X at
step 821 instead of 825, RSN 1633-X at 571 instead of 598, and RSN 1633-Y at
511 instead of 533. Refined-mesh maximum CM drifts were only 0.744%, 0.973%
and 0.949%, while the largest section components reached 7.060, 41.406 and
12.896 1/m respectively.

This demonstrates spatial non-objectivity of the current local fibre model.
The result and source check are documented in
`validation/SPEAR_NLTHA_MESH_OBJECTIVITY_2026-11-02.md`. No mesh variant is
accepted, and the production NLTHA/FVD/PBEE gate remains closed.

## Source recovery update — 2026-11-03

The missing Ljubljana OpenSees package was identified exactly as
`SPEAR-Post-Test-Model.zip`. The live URL is now 404; Wayback has no capture of
the ZIP and preserves only the IKPIR project error page and workshop PDF;
GitHub global code search found no copy. This different post-test model would
have served only as a common-input cross-check, not as a substitute for UIUC
ZEUS-NL.

An independent SPEAR paper confirms that the bent beam bars are inclined at 45
degrees. Their start/end coordinates remain unrecovered, so the bar transition
still cannot be reconstructed uniquely. No model value was changed. The audit
is documented in `validation/SPEAR_SOURCE_RECOVERY_UPDATE_2026-11-03.md`.

## Regularized hinge candidate — 2026-11-03

A non-calibrated `HingeMidpoint` candidate now uses one force-based element per
physical member and `Lp=0.08L+0.022fydb`, with published `fy=458.67 MPa` and
`db=12 mm`. Existing fibre sections, geometry, masses, gravity, P-Delta and
materials are unchanged. Initial periods differ from the distributed baseline
by only 0.18--0.21%.

All four pushover directions were executed. Peak errors are -2.28% (+X),
-3.79% (-X), +13.98% (+Y) and +3.51% (-Y); three reach 200 mm and +Y reaches
197 mm. The three low-drift NLTHA failures all disappear: RSN 900-X, RSN
1633-X and RSN 1633-Y complete every step with zero solver fallback.

This is a **REGULARIZED CANDIDATE**, not final validation. The full partial-21
suite, curve/mechanism comparison and hinge-integration sensitivity remain
required before reopening FVD/PBEE. Full evidence is in
`validation/SPEAR_REGULARIZED_HINGE_CANDIDATE_2026-11-03.md`.

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

## Regularized hinge candidate and 21-pair robustness gate — 2026-11-04

The spatially non-objective distributed-fibre mesh has been supplemented by a
non-calibrated regularized candidate: one force-based member per physical
member with `HingeMidpoint` integration and physical hinge length
`Lp = 0.08 L + 0.022 fy db`. Existing fibre sections, geometry, offsets,
materials, mass, gravity and damping are unchanged.

Initial periods change by only -0.18% to -0.21% relative to the distributed
model. Four-direction pushover peak errors against Fig. 2.8 are -2.28%,
-3.79%, +13.98% and +3.51% for +X, -X, +Y and -Y, respectively; +Y remains an
open physical discrepancy and was not calibrated away.

The full available 21-pair bidirectional suite completed 18 records (85.7%).
The maximum drift among complete records was 3.773%, with zero solver fallback
attempts in all 18. RSN953, RSN1244 and RSN1602 stopped only after reaching
last-converged maximum drifts of 69.47%, 70.55% and 67.65%, respectively, and
are classified conservatively as instability-compatible nonconvergence rather
than confirmed collapse. This closes the prior low-drift numerical-localization
blocker for the candidate but does not constitute final physical validation.

Remaining gates are full pushover curve/mechanism comparison (especially +Y),
admissible hinge-integration sensitivity, and explicit treatment of the
unrecovered ZEUS-NL `con2` tensile input and exact bent-bar transition data.
FVD/PBEE production work remains closed.

### Hinge quadrature sensitivity — 2026-11-04

The full `HingeMidpoint` curves have MAE values of 42.10, 50.57, 43.60 and
33.87 kN for +X, -X, +Y and -Y. Secant stiffness at 20 mm is overpredicted by
22.63--28.67%, and at 40 mm by 18.94--24.39%; therefore good peak-strength
agreement does not imply full curve-shape agreement.

Replacing only `HingeMidpoint` by `HingeRadauTwo` while preserving physical
hinge lengths and every model input produced stops at +51.5, -48.5, +103.5 and
-80.0 mm. Peak errors became -13.70%, -14.99%, -6.19% and -13.17%, with 31--56
fallback attempts. Initial periods changed negligibly. The admissible
integration-sensitivity gate therefore **fails**: the candidate is not yet a
formulation-independent physical validation. FVD/PBEE remains closed pending
member-level mechanism recording and resolution of source-data limitations.

### Member-level mechanism recorders — 2026-11-04

Regularized pushovers now retain peak storey drifts and ranked member plastic
rotations. +X, -X and +Y are dominated by all nine first-storey columns; their
peak first-storey drifts are 5.864%, 6.450% and 4.798%, respectively. -Y spreads
response between storeys 1 and 2 (3.291% and 2.971%) and includes first-storey
beam B10 among the ten largest plastic rotations. Full rankings are stored as
machine-readable `*_mechanism.json` files.

This demonstrates rather than assumes the first-storey mechanism in three
directions. It does not close physical acceptance because a numerical
member-by-member ZEUS-NL or experimental hinge sequence has not been recovered,
and the hinge-quadrature sensitivity gate remains failed.

MAE 04-03 Fig. 2.10 provides a qualitative mechanism gate: X should localize
in the first storey after peak, whereas C6 should keep first- and second-storey
drifts close in Y. The candidate passes this comparison for both X directions
and for -Y, but fails it for +Y (4.798% versus 1.242% drift in storeys 1 and 2).
The +Y strength error is therefore accompanied by the wrong damage
distribution. This is now the principal physical blocker, with C6 strong-axis
response and the missing ZeusNL concrete tensile law as direct audit targets.

### Section 2 no-diaphragm regularized baseline — 2026-11-05

The prior robust candidate retained a rigid diaphragm that is not part of the
Section 2 model producing Fig. 2.8. The regularized model was rerun with this
constraint removed and C3 displacement control. Peak errors are -7.42%,
-11.80%, -10.41% and -19.05% for +X, -X, +Y and -Y; curve MAE values are
21.62, 22.02, 36.68 and 72.77 kN. This is generally a much closer complete
curve-shape result than the rigid-diaphragm candidate, despite conservative
peak strengths.

Crucially, +Y storey drifts become 1.645%, 1.608% and 0.927%, satisfying the
published qualitative mechanism that C6 keeps the first two storeys close.
The implementation default is therefore changed to no diaphragm for Fig. 2.8
validation. The 18/21 NLTHA completion result obtained with a rigid diaphragm
is retained as a numerical experiment only and is not transferable to the
source-correct baseline. Downstream FVD/PBEE remains closed.

### Corrected executable acceptance gate and Y-asymmetry audit — 2026-11-05

The executable acceptance gate previously read the superseded
rigid-diaphragm result and incorrectly authorized downstream NLTHA/FVD. It now
reads only `regularized_hinge_midpoint_no_diaphragm`, checks the no-diaphragm
metadata and the published +Y first/second-storey mechanism, and returns
`FAIL`. All four modal errors are within 10%; +X, -X and +Y peak errors are
within 15%; -Y fails at -19.05%. Downstream work is therefore blocked.

At the +Y peak, C6 supplies 96.04 kN of 351.82 kN and its first-storey basic
axial force is -169.40 kN. At the -Y peak, C6 supplies -135.84 kN of
-367.54 kN and its axial force is -344.03 kN. The model's total Y-direction
strength asymmetry is only 15.72 kN, versus 61.32 kN in Fig. 2.8. Thus the
remaining peak failure is concentrated in the compression-favoured -Y branch
and is consistent with the unresolved `con2` axial-flexural material mapping;
it is not evidence for rotating C6 or restoring a rigid diaphragm.

### Section 2 continuous compression-envelope sensitivity — 2026-11-05

The source-bounded `ConcreteCM` compression envelope was combined with the
no-diaphragm `HingeMidpoint` model, retaining zero tension and changing no
geometry, reinforcement, mass, gravity or load pattern. All four cases reached
+/-200 mm. Pre-gravity periods became 0.50381, 0.44527, 0.37122 and 0.17658 s.

| Case | Peak (kN) | Peak error | Curve MAE (kN) |
|---|---:|---:|---:|
| +X | 333.413 | -5.91% | 35.55 |
| -X | 325.940 | -11.27% | 31.07 |
| +Y | 358.380 | -8.74% | 24.68 |
| -Y | 375.144 | -17.37% | 62.22 |

The Y peak difference is 16.76 kN, versus 15.72 kN for the candidate and
61.32 kN in Fig. 2.8. C6 contributes 102.77 kN at +Y and -146.24 kN at -Y.
Therefore the published-point continuous compression envelope improves
convergence and modal periods but does not recover the missing directional
asymmetry. It is retained as a rejected sensitivity, not a production update.
The remaining source priorities are the original Fig. 2.3 bent-bar transition,
the exact gravity load-point ledger controlling C6 axial force, and the full
ZeusNL `con2` tension/unloading implementation.

### Source-bounded 45-degree bent-bar sensitivity — 2026-11-05

The independently documented 45-degree bar inclination was converted to a
geometric 0.442 m horizontal transition using the 0.500 m beam depth and the
published cover/stirrup/bar diameters. This value replaced only the beam hinge
length; column regularization and every physical input remained unchanged.
All four cases reached +/-200 mm.

| Case | Peak (kN) | Peak error | Curve MAE (kN) |
|---|---:|---:|---:|
| +X | 327.147 | -7.68% | 20.66 |
| -X | 324.829 | -11.57% | 22.67 |
| +Y | 350.012 | -10.87% | 43.48 |
| -Y | 366.601 | -19.25% | 72.85 |

The Y-direction peak difference is 16.59 kN, again far below the published
61.32 kN and essentially unchanged from the candidate's 15.72 kN. The +Y
first/second-storey drifts remain close (3.006% and 2.594%). Therefore the
source-bounded 45-degree transition does not explain the missing asymmetry and
is rejected as a production replacement. A dimensioned original transition
would still improve exact reconstruction, but its plausible geometric proxy
is no longer a leading explanation for the -Y strength deficit.

### Engineering acceptance decision — 2026-11-05

The source-correct no-diaphragm candidate is accepted for the defined FVD/PBEE
research scope using a 10% absolute modal-period limit, a 20% absolute peak
base-shear limit, and mandatory qualitative mechanism/pattern checks. This is
an engineering benchmark validation, not an exact reconstruction of the
unavailable UIUC ZeusNL input deck or a pointwise reproduction of Fig. 2.8.

All four modal checks, all four pushover peak checks and all qualitative checks
pass. The governing -Y error is -19.05%, close to the limit, and its deficient
directional asymmetry must be retained as explicit model-form uncertainty.
Baseline NLTHA and FVD model development are now authorized. Optimization,
MSA and FEMA P-58 remain closed pending their own reproducibility and
acceptance gates.


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


## Table 3.1 section-level audit — 2026-10-18

An independent Eq. 3.2 strain-compatibility calculation now covers all 24
regular-column/story yield curvatures and both C6 bending axes. With the
published compression model and no invented tensile law, regular-column yield
curvatures have 8.13% mean absolute error and 12.17% maximum absolute error.

C6 weak-axis calculations are 13.90, 13.51 and 13.11 x10^-6 rad/mm, close in
order to the first unlabelled published subcolumn. The corresponding direct
strong-axis values are 4.16, 4.05 and 3.93 x10^-6 rad/mm; no Table 3.1 C6
subcolumn has that order of magnitude. Together with the modal falsification
of an axis swap, this isolates a source/convention anomaly in Table 3.1 and
closes C6 rotation as an admissible corrective action.

The remaining material blocker is narrower: the numerical SPEAR tensile input
and exact tensile branch of ZeusNL `con2`. The manual and later literature
confirm that tensile strength is a required input, but the only newly located
figure is a generic 30 MPa concrete example and is not valid evidence for the
25 MPa SPEAR model. No material value has been calibrated or substituted.


## UIUC longitudinal-mesh correction — 2026-10-20

The nonlinear model previously used a single five-point Lobatto member, which
MAE 04-03 Table 2.8 associates with the University of Rome OpenSees model
rather than the target UIUC ZeusNL model. The reconstruction now uses four
subelements per member (0.15L/0.35L/0.35L/0.15L), each with second-order
Gaussian integration, consistent with the UIUC element formulation and the
later documented ZeusNL SPEAR mesh.

The correction leaves fibre pre-gravity periods nearly unchanged
(0.49035, 0.42989, 0.36069 and 0.16964 s) but changes plastic localization and
resolves the dominant peak-strength discrepancy. Adaptive displacement control
now reaches +/-200 mm in every direction without changing structural inputs.

| Case | Fig. 2.8 peak (kN) | OpenSees peak (kN) | Peak error | Curve MAE (kN) |
|---|---:|---:|---:|---:|
| xp100 | 354.363 | 349.132 | -1.48% | 51.18 |
| xn100 | 367.335 | 357.950 | -2.55% | 65.67 |
| yp100 | 392.689 | 435.569 | +10.92% | 50.86 |
| yn100 | 454.009 | 464.394 | +2.29% | 57.34 |

This is a major improvement from the previous +45% to +61% peak errors, but it
does not complete validation. Initial stiffness remains excessive, peaks occur
too early and post-peak degradation is too strong. The exact ZeusNL `con2`
tensile/compression-tail equivalence and the dimensioned bent-bar transition
remain open source-data gates. FVD and all downstream work remain blocked.


## ZEUS-NL `con2` archive and continuous-envelope sensitivity — 2026-10-21

The official Google Code archive was audited reproducibly.  It contains the
ZEUS-NL manual and SVN metadata but zero non-SVN files in the public `trunk`;
the `con2` source subroutine is therefore not recoverable from that archive.
The manual confirms four inputs (`fc`, `ft`, `eco`, `K`) but does not supply the
SPEAR-specific numerical `ft`.

A non-accepted `ConcreteCM` sensitivity used only the published compression
constraints and retained zero tension.  Run `39705499820` completed all four
directions to +/-200 mm.  Results are now versioned separately from production:

| Case | Fig. 2.8 peak (kN) | Sensitivity peak (kN) | Peak error | Curve MAE (kN) |
|---|---:|---:|---:|---:|
| xp100 | 354.363 | 352.955 | -0.40% | 26.40 |
| xn100 | 367.335 | 359.942 | -2.01% | 27.13 |
| yp100 | 392.689 | 468.647 | +19.34% | 74.81 |
| yn100 | 454.009 | 496.827 | +9.43% | 51.27 |

Pre-gravity periods are 0.50376, 0.44181, 0.36982 and 0.17426 s;
post-gravity periods are 0.53654, 0.48278, 0.39933 and 0.18093 s.  The
sensitivity improves the X curve shape but worsens Y, and therefore is not a
valid global material replacement.  The production model remains unchanged.

The active acceptance blockers are the unrecovered SPEAR `con2` tensile input
and tensile branch, the undimensioned Fig. 2.3 bent-bar transition, and the lack
of published quantitative mode-shape ordinates.  SPEAR-M0 remains **NOT
VALIDATED**; FVD, optimization, NLTHA/MSA and FEMA P-58 remain blocked.

## External source-recovery audit — 2026-10-27

The search was extended beyond MAE 04-03 and the ZeusNL archive.  JRC 52127
states that the SPEAR database missed the experimental `Config Master`
input/test/library files and raw-result package later retained for other ELSA
projects.  This establishes an incomplete ELSA archive, but does not establish
that every partner's analytical input deck was destroyed.

The 2005 SPEAR workshop paper by Fajfar et al. identifies a separate Ljubljana
post-test report that included an OpenSees input file.  That concentrated-
plasticity model is not the target UIUC ZeusNL fibre model and its parameters
cannot be substituted.  It remains a legitimate recovery lead for common
geometry, mass and test metadata.  No public search recovered the UIUC ZeusNL
`.dat`, the SPEAR-specific `con2` tensile input, a dimensioned bent-bar
transition or numerical mode-shape ordinates.

The full search ledger and source boundaries are recorded in
`validation/SPEAR_SOURCE_RECOVERY_LOG_2026-10-27.md`.  Missing parameters will
not be back-fitted from Fig. 2.8.

## Reproducibility and pushover-pattern CI audit — 2026-10-27

The modal audit previously contained a stale copied elastic period vector.
It now rebuilds the current source-ledger elastic model before the fibre model,
so geometry or mass corrections propagate automatically.  Reproduced values
with OpenSeesPy 3.8.0.0 are:

| State | T1 (s) | T2 (s) | T3 (s) | T4 (s) |
|---|---:|---:|---:|---:|
| Published | 0.51000 | 0.46000 | 0.40000 | 0.18000 |
| Current elastic | 0.51446 | 0.44775 | 0.37304 | 0.17797 |
| Fibre pre-gravity | 0.49035 | 0.42989 | 0.36069 | 0.16964 |
| Fibre post-gravity | 0.54448 | 0.48683 | 0.40139 | 0.18326 |

The fibre pre-gravity periods are 3.31% to 4.69% below the corresponding
current elastic periods.  Gravity then increases them by 8.03% to 13.24%.
Therefore the fibre and elastic modal analyses are not exactly equivalent:
material tangents, reinforcement and the gravity equilibrium state matter.

A new solver-independent gate verifies all four `xp100/xn100/yp100/yn100`
patterns.  Each global normalized resultant is exactly +1 or -1, every floor
resultant follows Eq. 2.5, and the three spatial Fig. 2.7 forces retain a
nonzero torsional moment about that floor's centre of mass.  The workflow now
runs this gate, pins OpenSeesPy 3.8.0.0, and invokes the four-direction driver
only once with its valid case names.

## Pre-peak secant-stiffness comparison — 2026-10-27

The Fig. 2.8 digitization does not contain a reliable origin point in every
panel, so no pixel-derived tangent stiffness is claimed.  The comparison tool
now reports reproducible secant stiffness at common 20 and 40 mm roof
displacements:

| Case | Error at 20 mm | Error at 40 mm |
|---|---:|---:|
| xp100 | +20.94% | +18.48% |
| xn100 | +24.76% | +18.35% |
| yp100 | +22.99% | +21.94% |
| yn100 | +26.77% | +24.19% |

The excess is systematic in all four directions and precedes the capacity
peak.  Matching peak resistance alone is therefore insufficient: the current
production fibre model remains too stiff over the common pre-peak range.  No
material or geometric input was changed to reduce this error.

## Beam-section initial-stiffness audit — 2026-10-27

An independent transformed-section audit now compares every B1--B12 T-section
used by the elastic and production fibre models.  It exposes a constitutive
equivalence issue rather than a geometry or mass discrepancy:

- the source-ledger elastic modulus is 23.5 GPa;
- the initial tangent implied by the production `Concrete02` inputs is
  `2*fpc/epsc0 = 25.0 GPa`, 6.38% higher;
- including the published Phi12 steel fibres gives initial fibre-section EI
  values 11.88% to 14.31% above the corresponding concrete-only elastic EI at
  beam ends, and 15.01% to 15.96% above it in the interior sections.

The direction and magnitude are consistent with the fibre pre-gravity periods
being 3.31% to 4.69% shorter than the current elastic periods.  Thus the two
models should not be expected to have identical modal results: their material
tangents and steel contribution are not stiffness-equivalent.

This finding also narrows the nonlinear discrepancy.  The section-level
initial mismatch can explain part, but not all, of the 18%--27% pre-peak global
secant excess.  `Concrete02` cannot prescribe the published elastic modulus
independently of its peak stress and strain.  Replacing it by a different law
without recovering the full ZeusNL `con2` tensile and compression branches
would still be an unverified material substitution, so production remains
unchanged.

## Gravity-state application audit — 2026-10-27

The nodal mass ledger and the nonlinear gravity-loading pattern must be treated
as different objects. MAE 04-03 Section 2.2.4 explicitly states that slab and
slab self-weight are distributed to the nearest beams according to Fig. 2.6,
using several loading points along each beam. Only the dynamic masses are
subsequently condensed to beam-column connections.

The current OpenSees nonlinear `gravity()` function instead applies the full
recovered Table 3.1 floor weight vertically at the nine beam-column joints.
This reproduces column axial totals but gives the beams no distributed gravity
bending before lateral loading. Consequently it cannot reproduce the original
beam moment, cracking and tangent-stiffness state at the start of pushover.
This is a physical-model discrepancy and a plausible contributor to the
systematic 18%--27% pre-peak secant-stiffness excess.

Fig. 2.6 defines the tributary geometry but does not tabulate the exact ZeusNL
loading-point coordinates or magnitudes; the text only says that their number
depends on beam length. A geometrically reconstructed distributed-load
sensitivity may quantify the effect, but cannot be promoted to the production
source lock without recovering or independently verifying that discretization.
The acceptance gate now explicitly includes the original beam gravity
loading-point ledger.

### Fig. 2.6 beam-gravity sensitivity

A non-accepted numerical reconstruction assigns each slab cell to its nearest
B1--B12 centreline, condenses that tributary load to the existing four-element
beam stations, retains column self-weight at joints and scales only to close
the exact Table 3.1 floor totals. Equilibrium closes to machine precision at
659.63, 659.66 and 615.95 kN.

| Case | Reached (mm) | Peak error | Secant error 20 mm | Secant error 40 mm |
|---|---:|---:|---:|---:|
| xp100 | 200 | -3.98% | +17.82% | +17.23% |
| xn100 | 200 | -5.60% | +17.33% | +15.72% |
| yp100 | 120 | +6.53% | +22.67% | +21.39% |
| yn100 | 180 | +0.87% | +20.84% | +22.07% |

Compared with joint-only gravity, distributing gravity to beams improves most
peak errors and the X-direction pre-peak stiffness. It does not remove the
systematic stiffness excess. The hypothesis that gravity-state application
alone explains Fig. 2.8 is therefore rejected. Production remains unchanged
because Fig. 2.6 does not publish the original ZeusNL loading-point ledger.

## Section 2 diaphragm-definition audit — 2026-10-27

The target and the current OpenSees model did not use the same floor
idealization. MAE 04-03 Section 2.2.2 states that slabs are omitted and only
their T-beam effective width is retained. Section 5.2 then says explicitly
that the rigid diaphragm was introduced later as a refinement to the Section 2
model. Figure 2.8 belongs to the Section 2 pre-test analysis, whereas the
current production reconstruction constrains every floor as rigid in plane.

A non-accepted source-bounded sensitivity removes only the rigid-diaphragm
constraints, keeps masses at the published beam-column connections, and uses
C3 as roof control point. C3 is the roof-displacement location identified in
Figs. 2.17 and 4.3. No stiffness or strength parameter is fitted.

| Case | Reached (mm) | Peak error | Secant error 20 mm | Secant error 40 mm |
|---|---:|---:|---:|---:|
| xp100 | 200 | -8.59% | -8.42% | -6.13% |
| xn100 | 100 | -9.55% | -2.55% | -4.57% |
| yp100 | 80 | -11.94% | -9.26% | -9.01% |
| yn100 | 80 | -16.86% | -10.46% | -9.57% |

Removing the diaphragm reverses the production model's +18% to +27% pre-peak
stiffness excess, but underpredicts all four peak strengths. The pre-gravity
periods are 0.49138, 0.43410, 0.36266 and 0.17218 s. After the existing
joint-only gravity load they lengthen to 0.71220, 0.67839, 0.51642 and 0.37794
s. This excessive shift shows that diaphragm removal cannot be assessed
independently from the missing Fig. 2.6 beam-gravity state.

### Combined no-diaphragm plus reconstructed Fig. 2.6 gravity

The combined sensitivity was run to 100 mm in all four directions:

| Case | Peak error | Secant error 20 mm | Secant error 40 mm |
|---|---:|---:|---:|
| xp100 | -9.82% | -12.61% | -5.77% |
| xn100 | -13.48% | -17.33% | -11.09% |
| yp100 | -12.20% | -7.42% | -4.78% |
| yn100 | -20.26% | -16.36% | -12.69% |

The combined change softens the response further and is not accepted. Its
post-gravity periods are 0.76557, 0.74261, 0.55825 and 0.47322 s, incompatible
with the published elastic periods. The source evidence nevertheless requires
the final Fig. 2.8 reconstruction to omit a rigid diaphragm; the remaining
underprediction must be resolved through the exact ZeusNL concrete tensile
law and original beam-gravity loading ledger, not by restoring an incompatible
constraint or fitting strength. Production remains unchanged.

## Accepted Section-2 baseline NLTHA — 2026-11-06

The accepted no-diaphragm Section-2 model was run bidirectionally for all 21
available FEMA-P695 pairs at unscaled as-recorded intensity. The formulation
was `HingeMidpoint`; damping was 5% Rayleigh damping anchored to initial modes
1 and 3. No structural, record or damping parameter was calibrated.

Eighteen pairs completed every requested step. Their median maximum storey
drift was 1.586%; the maximum was 4.175% for RSN1602. RSN953, RSN1158 and
RSN1244 stopped after last-converged maximum drifts of 46.56%, 118.45% and
128.56%, respectively. Repetition with element diagnostics reproduced all
three stops. They are classified conservatively as instability-compatible
nonconvergence, not as complete EDP histories or formally proven collapse.

This closes the moderate-drift numerical-convergence concern for the accepted
baseline: no incomplete case stopped below 10% drift. Compact per-pair JSON,
logs, the aggregate summary and EDP table are in
`results/SPEAR/fvd/baseline_section2_hinge_midpoint_partial21/`. Raw response
CSV histories are excluded from Git but are reproducible from the licensed
PEER traces and committed manifest. The detailed audit is
`validation/SPEAR_SECTION2_BASELINE_NLTHA_2026-11-06.md`.
