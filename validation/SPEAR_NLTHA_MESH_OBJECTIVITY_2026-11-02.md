# SPEAR-M0 NLTHA mesh-objectivity audit — 2026-11-02

## Purpose and admissible change

The three low-drift directional failures were repeated after dividing every
published 0.15L/0.35L/0.35L/0.15L subelement into two equal subelements. The
section assigned to each original interval, material parameters, integration
order, geometry, rigid offsets, masses, gravity, damping and records were held
constant. This eight-subelement model is diagnostic only; it is not a proposed
replacement for the MAE 04-03 four-subelement discretization.

The check is required because local strain-softening frame formulations do not
automatically provide a physical localization length. OpenSees documents the
gradient-inelastic element specifically as a formulation intended to eliminate
localization and response-objectivity problems by adding nonlocal relations and
a characteristic length. Introducing such a length here would require physical
evidence and is therefore not done in this audit.

## Modal control

| State | Mesh | T1 (s) | T2 (s) | T3 (s) | T4 (s) |
|---|---|---:|---:|---:|---:|
| pre-gravity | 4 subelements | 0.490348 | 0.429894 | 0.360692 | 0.169641 |
| pre-gravity | 8 subelements | 0.490348 | 0.429896 | 0.360693 | 0.169641 |
| post-gravity | 4 subelements | 0.544480 | 0.486829 | 0.401386 | 0.183260 |
| post-gravity | 8 subelements | 0.545307 | 0.488116 | 0.402204 | 0.183528 |

The pre-gravity differences are below 0.0004%, confirming that the refinement
does not change the elastic structure. Post-gravity differences remain below
0.27%, reflecting a small mesh dependence of the nonlinear gravity state.

## Transient results

| Case | Baseline stop | Refined stop | Baseline max CM drift | Refined max CM drift | Refined largest section component |
|---|---:|---:|---:|---:|---:|
| RSN 900 X | 825 | 821 | 1.180% | 0.744% | 7.060 1/m |
| RSN 1633 X | 598 | 571 | 1.287% | 0.973% | 41.406 1/m |
| RSN 1633 Y | 533 | 511 | 1.193% | 0.949% | 12.896 1/m |

All three refined analyses remain incomplete despite adaptive subdivision to
1/16 of the record interval. Refinement makes every stop earlier, reduces the
global drift reached before failure, changes the controlling element, and
produces extreme local section deformation. RSN 1633-X is especially decisive:
the largest section component rises to 41.406 1/m while centre-of-mass drift is
still below 1%.

## Concrete-model source check

The ZEUS-NL manual confirms that `con2` requires compressive strength, tensile
strength, crushing strain and confinement factor. Its 2.2 MPa tensile strength
is explicitly a typical example paired with 20 MPa concrete and K=1.2; it is
not the SPEAR input. MAE 04-03 gives 25 MPa and K=1.01 but does not report the
numerical tensile input. OpenSees `Concrete02` instead uses the Yassin law, a
user-defined unloading ratio and linear tensile softening; its documented
initial tangent is `2*fpc/epsc0`. The two cyclic laws cannot be declared
equivalent from the recovered information.

Primary documentation:

- MAE Center ZEUS-NL manual: <https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/zeus-nl/Manual_v1.8.9.pdf>
- OpenSees Concrete02: <https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Concrete02.html>
- OpenSees gradient-inelastic element: <https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/gradientInelasticBeamColumn.html>
- Martinez-Rueda and Elnashai (1997), *Materials and Structures* 30:139-147.

## Decision

The current local fibre model fails the spatial-objectivity gate. The low-drift
stops are not valid physical collapse predictions, and no tested element,
integration or mesh variant is accepted. Production NLTHA, FVD, fragility and
PBEE remain blocked.

The remaining defensible routes are: recover the original SPEAR ZEUS-NL input
and `con2` implementation; or define and validate a regularized OpenSees model
from independent material/member evidence. Choosing a characteristic length or
tensile law to make these three records converge would be calibration and is
prohibited.
