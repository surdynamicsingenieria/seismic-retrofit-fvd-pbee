# Jeong–Elnashai SPEAR nonlinear source-lock and acceptance gate

Status: **BLOCKED — diagnostic runs only**. Last audited: 2026-10-08.

## Baseline preserved
- Modal benchmark MAE 04-03 Table 2.4: 0.51, 0.46, 0.40, 0.18 s.
- Last modal reconstruction: 0.54352257, 0.46611427, 0.35627241, 0.18257494 s.
- New nonlinear +X diagnostic: 0.53619469, 0.45973746, 0.35181913, 0.17856697 s.
- +X diagnostic reached 0.11989658 m, peak |Vb| = 483.76647 kN. **Not benchmark validated**.
- First/third modal errors in nonlinear model: +5.14% / -12.05%; investigate shape participation before accepting modal equivalence.

## Model differences that invalidate a quantitative capacity claim
1. **Beams remain elastic T-sections** in `spear_m0_jeong_elnashai_nonlinear.py`. Thus beam plasticity, degradation, cyclic/postpeak strength cannot be claimed. Do not copy Stratan–Fajfar end hinges.
2. **Column reinforcement is provisional** (four Ø12 in 250×250; ten Ø12 in C6), not a verified floor-by-floor MAE 04-03 schedule. Source verification required before accepting M–M–N behavior.
3. **Gravity uses equal per-joint allocation**, rather than the slab-to-beam distribution in MAE 04-03 Fig. 2.6. Gravity axial-force and P–Δ response are consequently provisional.
4. **Mass is concentrated at three floor CM masters** using published floor mass and polar inertia. Source-lock requires documenting equivalence to nodal beam-column masses for the intended diaphragm formulation.
5. The current run **redefines analysis constraints/numberer/system after gravity**, yielding OpenSees warning `can't set handler after analysis is created`. Before interpreting nonlinear convergence, call `ops.wipeAnalysis()` between gravity and pushover and check gravity equilibrium.
6. Pushover loading currently uses **mode 1 projected onto requested axis**, which is not necessarily the controlling translational mode in a torsionally coupled building. Verify eigenvector participation and reproduce the actual Fig. 2.8 load patterns.
7. Current recovery step can accept one quarter of a nominal displacement increment without completing the remaining fraction; therefore final displacement is not exactly the requested target. Record accepted increment, retry path and failure cause.

## Required primary-source extraction (MAE Center Report 04-03)
- Table/figures specifying reinforcement for B1–B12 by storey and for columns C1–C9 by storey: bar positions, diameters, cover, transverse reinforcement, material grade.
- Fig. 2.6 slab-to-beam and beam-to-column tributary gravity loading, including nodal force and eccentricity.
- Fig. 2.8 digitized xp100, xn100, yp100, yn100 curves, with axes/units and traceable digitization files.
- Fig. 2.2/2.4 connection geometry and offsets (especially C6, B5, B6, B10); verify actual physical/analytical member correspondence.

## Acceptance sequence
1. Complete source table, nodal mass/gravity ledger and modal shape/participation audit.
2. Replace elastic T beams with nonlinear fiber sections and verified longitudinal/transverse reinforcement.
3. Correct analysis reset, displacement stepping and force equilibrium checks.
4. Re-run +X with CSV + log + machine-readable metadata, then overlay digitized xp100 reference.
5. Run -X, +Y, -Y with independent direction-appropriate load patterns and overlays.
6. Compare initial stiffness, peak base shear, drift at peak, softening, first-storey mechanism, C6 compression/tension asymmetry and numerical convergence.
7. Only after independent quantitative sign-off may `SPEAR_VALIDATION_STATUS.md` be changed to validated.

**No FVD, optimization, NLTHA/MSA or FEMA P-58 before all gates pass.**
