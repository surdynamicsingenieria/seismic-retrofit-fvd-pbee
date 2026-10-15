# SPEAR ZeusNL concrete source audit - 2026-10-14

## Findings

MAE 04-03 states that the pre-test model used the ZeusNL uniaxial constant
confinement concrete model based on Mander et al. and modified by
Martinez-Rueda and Elnashai. It identifies four inputs: unconfined compressive
strength, tensile strength, crushing strain and confinement factor.

For SPEAR, MAE 04-03 explicitly gives:

- unconfined compressive strength: 25 MPa;
- confinement factor: 1.01;
- sparse stirrups with almost negligible confinement.

It does not give a numerical tensile strength in Section 2.2.3.

The ZeusNL User Manual, Appendix A, confirms that `con2` requires `fc`, `ft`,
`eco` and `k`. Its table lists 20 MPa, 2.2 MPa, 0.002 and 1.2 as **typical
values**. These are software examples and not the SPEAR input deck. Therefore
2.2 MPa cannot be adopted as the SPEAR tensile strength without the original
input or another primary project source.

Source: ZeusNL User Manual, Appendix A, pp. 87-88:
https://www.researchgate.net/profile/Vassilis_Papanikolaou/publication/32962835_Zeus_NL_-_A_System_for_Inelastic_Analysis_of_Structures/data/53ddd1520cf2cfac99291864/32-Zeus-NL-A-program-for-inelastic-dynamic-analysis-of-structures.pdf

## Eigenvalue-state decision

The ZeusNL manual states that loading phases are not needed for eigenvalue
analysis. Accordingly, the MAE 04-03 elastic periods and first mode used in
Eq. 2.5 are treated as pre-gravity eigenvalue results. The nonlinear OpenSees
driver now stores both states but uses the pre-gravity first mode for the
pushover force distribution.

## Blocker

The current OpenSees `Concrete02` mapping uses zero tensile strength. This is
not equivalent to ZeusNL `con2` and is retained only as an explicit diagnostic
placeholder. No nonzero value will be selected from the capacity curves.
