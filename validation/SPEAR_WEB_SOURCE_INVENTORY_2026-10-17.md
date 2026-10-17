# SPEAR web-source inventory — 2026-10-17

## Scope

Targeted search for primary or technically traceable sources capable of resolving
the two remaining source locks in the Jeong–Elnashai SPEAR-M0 reconstruction:

1. the exact UIUC/ZeusNL nodal mass and gravity-load ledger; and
2. the numerical concrete tensile strength supplied to the ZeusNL `con2`
   material.

No value found below is adopted merely because it belongs to another SPEAR
partner model.

## Sources inspected

### Jeong and Elnashai, MAE Report 04-03

Primary validation source:

- https://mae.cee.illinois.edu/publications/reports/Report04-03.pdf

Confirmed:

- concrete `f'c = 25 MPa`, confinement factor `K = 1.01`;
- steel `fy = 459 MPa` for Phi12 and `377 MPa` for Phi20;
- `DL + 0.3LL` for gravity and seismic mass;
- mass distributed at beam-column connections;
- total mass stated as `1957 kN/g`;
- first-mode Eq. 2.5 floor pattern and Fig. 2.7 plan redistribution;
- `con2` requires a tensile-strength input, but the report does not disclose
  its numerical value.

The report contains the construction rule but not a numerical node-by-node mass
table or the original ZeusNL input deck.

### SPEAR International Workshop proceedings, 2005

Technical compilation:

- https://www.researchgate.net/publication/345732778_SPEAR_Seismic_Performance_Assessment_and_Rehabilitation_of_Existing_Buildings_INTERNATIONAL_WORKSHOP_An_event_to_honour_the_memory_of_Prof_Jean_Donea

The Jeong–Elnashai workshop paper confirms the same distributed-plasticity,
rigid-diaphragm, gravity/mass rules. It adds two important distinctions:

- the test water tanks represented gravity only; their plan distribution did
  not define analytical seismic mass;
- the applied design gravity load for the tanks was `1.1 kN/m2`.

A separate post-test CASTEM model in the same proceedings reports floor masses
of `67.264, 67.264, 62.804 t` and mass-centre coordinates. Their total is
`197.332 t = 1935.235 kN` at `g = 9.807 m/s2`, which is 1.112% below the
Jeong–Elnashai `1957 kN` total. These are therefore useful independent
cross-checks, but are not the missing UIUC nodal ledger and are not adopted.

The workshop version also uses measured post-test material strengths
(`f'c = 26.4 MPa`, `fy = 474/397 MPa`), different from the MAE 04-03
pre-test M0 values. Those values are not substituted into M0.

### Fardis (2002), structure-description report

Exact citation located repeatedly:

M. N. Fardis, *Design of an Irregular Building for the SPEAR Project —
Description of the 3-Storey Structure*, University of Patras, 2002.

The report itself was not recovered from an authoritative downloadable
location in this search. Secondary papers cite it for geometry and detailing,
but do not reproduce the missing UIUC ZeusNL nodal mass ledger or `con2`
input.

### Related SPEAR partner studies

Stratan–Fajfar and other partner models were inspected only for provenance.
Their masses and modeling assumptions differ from UIUC (including different
mass placement, live-load factors, rigid offsets, and constitutive models).
They remain excluded from acceptance inputs.

## Result

No searchable primary source exposed the original ZeusNL `.dat` deck, an
exact UIUC node-by-node mass/load table, or the numerical `ft` passed to
`con2`.

The current acceptance blockers therefore remain real and specifically
bounded:

- **Mass/gravity blocker:** original UIUC ZeusNL nodal input, or a reproducible
  Fig. 2.6 tributary ledger closing exactly to `1957 kN`.
- **Concrete blocker:** original `con2` material line or another primary
  Jeong–Elnashai source stating `ft`.

Until either is recovered, partner-model values and typical ZeusNL examples
must remain diagnostics only.