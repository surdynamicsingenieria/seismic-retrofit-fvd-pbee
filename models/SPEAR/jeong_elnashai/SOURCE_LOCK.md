# SPEAR-M0 Jeong-Elnashai benchmark — source lock

Status: **independent reconstruction in progress; not yet validated**

Primary source:
Jeong, S.-H. & Elnashai, A.S. (2004), *Analytical Assessment of an Irregular RC Full Scale 3D Test Structure*, MAE Center Report 04-03, University of Illinois at Urbana-Champaign.

## Rule
This benchmark is reconstructed from Report 04-03 as a self-consistent model. Do not import Stratan-Fajfar hinge parameters or tune physical parameters to match periods/capacity curves.

## Geometry / members
- 3-storey irregular RC bare frame.
- Physical beams B1-B12 only (Fig. 2.2 / Table 2.1).
- slab thickness 150 mm; slab omitted as explicit shell in analytical model.
- beams: 250 x 500 mm web; T-section flange used analytically.
- columns C1-C5, C7-C9: 250 x 250 mm.
- C6: 750 x 250 mm.
- stairs and infill walls omitted.
- rigid offsets at beam and column ends.
- C6 connection: rigid arms reproduce the offset between B5/B6 and C6 centrelines.

## Beam T-section effective widths (Table 2.1)
| Beam | beff mm | clear span mm |
|---|---:|---:|
| B1 | 442.5 | 2750 |
| B2 | 582.5 | 4750 |
| B3 | 635.0 | 2750 |
| B4 | 1055.0 | 5750 |
| B5 | 442.5 | 2750 |
| B6 | 652.5 | 5750 |
| B7 | 1055.0 | 5750 |
| B8 | 775.0 | 3750 |
| B9 | 1055.0 | 5750 |
| B10 | 775.0 | 3750 |
| B11 | 617.5 | 5250 |
| B12 | 582.5 | 4750 |

## Materials — pre-test source model
Concrete:
- f'c = 25 MPa.
- Mander-type concrete model.
- confinement factor K ≈ 1.01.

Steel (Table 2.2):
- Phi8: fy 467 MPa, fu 583.67 MPa, Es 206000 MPa, E2/E1 0.0044.
- Phi12: fy 458.67 MPa, fu 570.33 MPa, Es 206000 MPa, E2/E1 0.0032.
- Phi20: fy 376.67 MPa, fu 567.33 MPa, Es 206000 MPa, E2/E1 0.0056.

## Loads / mass
- gravity: DL + 0.3 LL.
- finishing load: 0.5 kN/m2.
- live load: 2.0 kN/m2.
- reinforced-concrete density used in report: 2.5 t/m3 (24.518 kN/m3).
- seismic mass distributed at beam-column connections.
- no viscous damping in the pre-test analytical model; hysteretic damping only.

## Nonlinear formulation to reproduce
- distributed plasticity.
- P-Delta considered.
- M-M-N interaction considered.
- rigid offsets at beam and column ends.
- fiber-based member response is the OpenSeesPy analogue to be used; discretization must be documented.

## Validation targets
### Modal gate — 3D model (Table 2.4 / Fig. 2.14)
- T1 = 0.51 s — combined torsion/X/Y.
- T2 = 0.46 s — combined torsion/X/Y.
- T3 = 0.40 s — combined torsion/X/Y.
- T4 = 0.18 s.

No stiffness/mass calibration is allowed solely to hit these values.

### Pushover gate
Reproduce Fig. 2.8 unidirectional curves:
- xp100 (+X)
- xn100 (-X)
- yp100 (+Y)
- yn100 (-Y)

Qualitative checks explicitly reported:
- Y is stiffer/stronger and more stable post-peak because of C6.
- yn is stronger than yp because C6 is predominantly in compression for yn and tension for yp.
- post-peak strength loss is mainly P-Delta-driven.
- X response develops first-storey drift concentration after peak.

Quantitative digitization of Fig. 2.8 must be stored separately before declaring the pushover gate passed.

## Validation sequence
1. source-lock geometry, reinforcement, loads and masses;
2. build elastic/nonlinear 3D OpenSeesPy model;
3. modal comparison;
4. +X / -X / +Y / -Y pushover;
5. quantitative comparison to digitized Fig. 2.8;
6. only after all gates pass may this model be considered a candidate SPEAR-M0 benchmark.

No FVD, optimization, NLTHA/MSA or FEMA P-58 before benchmark validation.


## Geometry/mass audit — exact-reconstruction gate (2026-10-06)

The first executable baseline is **not** the Jeong-Elnashai validation model. It intentionally remains diagnostic.

Verified directly from MAE 04-03:
- Figure 2.2 is the governing source for centerline geometry. Dimension strings include 3 m, 5 m, 1 m and 0.7 m in plan, with the irregular transverse dimensions 5.5 m, 5 m, 6 m and 4 m. Storey centerline spacing is 3 m and slab thickness is 0.15 m.
- Figure 2.4 requires rigid offsets at BOTH beam and column ends.
- B5 and B6 centerlines are not aligned with the C6 centerline. C6 therefore requires explicit rigid arms; a single coincident C6/B5/B6 joint is prohibited.
- Section 2.2.4: gravity = DL + 0.3LL; finishing = 0.5 kN/m2; design LL = 2.0 kN/m2; RC unit weight = 24.518 kN/m3.
- Slab gravity/self-weight is distributed to nearest beams (Fig. 2.6), then represented by multiple loading points/short beam elements.
- Seismic mass is gravity load divided by g=9807 mm/s2 and lumped at BEAM-COLUMN CONNECTIONS, not at one floor center.
- Table 2.3 explicitly states P-delta considered, distributed plasticity, centerline dimensions, rigid offsets, M-M-N interaction, no viscous damping.

### Prohibited carry-over from the diagnostic baseline
The provisional `PLAN` coordinates and single floor-center mass used in commit ce1b2e7 are not source-locked Jeong-Elnashai data and SHALL NOT be used for acceptance.

### Next executable gate
Before the next modal acceptance run:
1. reconstruct every joint centerline coordinate from Fig. 2.2;
2. create physical joint-face rigid offsets;
3. create separate B5/C6/B6 connection nodes and C6 rigid arms from Fig. 2.4;
4. distribute slab/member gravity according to Fig. 2.6;
5. condense the resulting seismic masses to the beam-column connections while retaining the rigid diaphragm kinematics;
6. report total floor mass, center of mass and polar mass moment for each floor before eigenanalysis.

No stiffness/mass scaling or period-target calibration is permitted.
