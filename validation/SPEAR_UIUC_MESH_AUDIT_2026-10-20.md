# SPEAR-M0 UIUC longitudinal-mesh audit — 2026-10-20

## Finding

The previous nonlinear diagnostic used one physical member with five
Gauss-Lobatto integration points. MAE 04-03 Table 2.8 identifies that as the
University of Rome OpenSees formulation, not the UIUC ZeusNL formulation whose
Fig. 2.8 curves are the validation target.

For UIUC, MAE 04-03 Sec. 2.1.2 states that the cubic elasto-plastic element
stiffness is integrated by second-order Gaussian quadrature and that shorter
elements are used near beam-column connections because element length controls
the capture of inelastic action. A later ZeusNL study of the same SPEAR model
documents the corresponding four-element member mesh as
`0.15L / 0.35L / 0.35L / 0.15L`, with two Gaussian points per element.

The OpenSees reconstruction now represents each beam and column by those four
subelements using two-point Legendre integration. Rigid offsets remain only at
the physical member ends. Beam end segments use the Fig. 2.3 end reinforcement
(4 top, 2 bottom bars); inner segments use section A-A' (2 top, 4 bottom bars).
This is a formulation correction, not a fitted strength parameter.

## Modal invariance check

The mesh correction leaves the initial fibre periods essentially unchanged:

| Mode | Previous fibre pre-gravity (s) | UIUC mesh (s) |
|---:|---:|---:|
| 1 | 0.490083 | 0.490348 |
| 2 | 0.429506 | 0.429894 |
| 3 | 0.360423 | 0.360692 |
| 4 | 0.169582 | 0.169641 |

This confirms that the capacity change is caused by longitudinal plasticity
representation rather than an accidental elastic-stiffness change.

## Full pushover results

All cases reach the requested 200 mm using adaptive displacement increments.
Gravity-state lateral drift is removed from the reported displacement. The
adaptive solver changes only numerical step size/algorithm and does not alter
the structural model.

| Case | Fig. 2.8 peak (kN) | OpenSees peak (kN) | Peak error | Peak displacement: reference / model (mm) | Curve MAE (kN) |
|---|---:|---:|---:|---:|---:|
| xp100 | 354.363 | 349.132 | -1.48% | 74.19 / 55.00 | 51.18 |
| xn100 | 367.335 | 357.950 | -2.55% | -82.58 / -57.50 | 65.67 |
| yp100 | 392.689 | 435.569 | +10.92% | 94.84 / 70.50 | 50.86 |
| yn100 | 454.009 | 464.394 | +2.29% | -147.74 / -57.50 | 57.34 |

Peak-strength errors previously ranged from +45% to +61%. The UIUC
longitudinal discretization therefore resolves the dominant strength
discrepancy without calibration.

## Remaining acceptance failures

SPEAR-M0 is still **not physically validated**:

- initial pushover stiffness is higher than Fig. 2.8;
- peak displacement occurs too early in all four directions;
- post-peak degradation is too strong, especially in negative Y;
- the numerical tensile strength and complete tensile branch of the original
  ZeusNL `con2` material remain unrecovered;
- Fig. 2.3 does not dimension the actual bent-bar transition, so assigning the
  end reinforcement over the complete outer 0.15L segment remains a
  source-supported but not dimensionally closed representation;
- the current OpenSees compression tail (`0.2fc` at strain 0.006) has not
  been demonstrated equivalent to the original `con2` law.

No FVD, optimization, NLTHA/MSA or FEMA P-58 work is permitted until the curve
shape and modal-shape gates are closed.

## Sources

- Jeong and Elnashai, MAE 04-03, Sec. 2.1.2, Fig. 2.3, Table 2.8 and Fig. 2.8.
- Ozcelik et al. (2022), *A case study on an innovative seismic performance
  evaluation procedure for irregular RC buildings*, Sec. 4, explicit ZeusNL
  four-element 0.15L/0.35L mesh and two-point Gaussian integration.
