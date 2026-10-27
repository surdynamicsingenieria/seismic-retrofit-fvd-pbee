# SPEAR source-recovery log — 2026-10-27

## Scope

This audit searched for the missing source inputs that prevent physical
acceptance of the Jeong--Elnashai/UIUC SPEAR-M0 reconstruction:

1. the SPEAR-specific `ft` and tensile branch used by ZeusNL `con2`;
2. a dimensioned location for the transition of the two bent-up beam bars;
3. numerical modal-shape ordinates; and
4. the original ZeusNL `.dat`/load input files.

No value from a different partner model was transferred into the production
model.

## Repositories and primary/technical sources checked

- Jeong and Elnashai, MAE Report 04-03, including the geometry, reinforcement,
  material-model, eigenvalue and pushover chapters already transcribed in the
  source ledger.
- The official archived ZeusNL manual and the complete Google Code archive.
  The archive contains 647 entries but no non-SVN file in public `trunk`; it
  does not expose the `con2` implementation or a SPEAR input deck.
- Bosi et al., *The ELSA database and what can be done regarding SERIES*, JRC
  52127 (2009), pp. 13--14.  The report says that the later ESECMaSE database
  stored pseudo-dynamic input/test/library files in `Config Master` and raw
  acquisition data in `Results Raw`, and states explicitly that all these
  pieces were missed in the SPEAR project.  This is direct evidence that the
  ELSA experimental archive is incomplete.  It is not evidence that every
  partner's independent analytical model file was destroyed.
- Fajfar et al., *Pre- and post-test mathematical modelling of the SPEAR
  building* (SPEAR Workshop, 2005).  This is a different University of
  Ljubljana model (CANNY/OpenSees concentrated plasticity), not the target
  UIUC ZeusNL fibre model.  It identifies a potentially recoverable 2005
  post-test report by Dolsek and Fajfar and says that report included an input
  file and detailed results.  Those inputs cannot be substituted into the
  UIUC model, but could independently verify common geometry, mass and test
  metadata.
- Public technical searches for combinations of `SPEAR`, `ZeusNL`, `.dat`,
  `input`, `con2`, `tensile strength`, and bent-up reinforcement.  No original
  Jeong--Elnashai SPEAR input deck or source-backed SPEAR `ft` was found.

## Findings

| Missing datum | Recovery result | Consequence |
|---|---|---|
| SPEAR ZeusNL `con2` tensile input `ft` | Not found. The manual's 2.2 MPa is only a generic 20 MPa example. | Zero tension and 2.2 MPa are both unverified for production. |
| Complete `con2` tensile/unloading branch | Not found; public source archive has no implementation. | OpenSees material equivalence cannot yet be asserted. |
| Bent-bar transition distance/angle | Not dimensioned in MAE 04-03 Fig. 2.3 and not recovered elsewhere. | Any transition coordinate remains a labelled sensitivity, not source truth. |
| Quantitative modal-shape ordinates | Not published/recovered. | Period errors can be measured; numerical shape error cannot. |
| UIUC ZeusNL SPEAR input deck | Not found in public ZeusNL or ELSA material. | Exact line-by-line reproduction remains blocked. |
| Ljubljana post-test input | Cited as included in Dolsek--Fajfar (2005), but report/input not recovered publicly. | Candidate source-recovery lead only; not a replacement for UIUC inputs. |

## Physical implications for the current model

The negative source result is consistent with the four-direction
`ConcreteCM` experiment: enforcing the published compression envelope while
leaving tension at zero improves both X curves but worsens both Y curves.  It
therefore cannot identify the missing tensile law indirectly, and must not be
accepted as calibration.

The JRC database statement also explains why repeated public-dataset searches
do not produce a complete experimental configuration package.  The model can
still be checked against published periods and Fig. 2.8, but those comparisons
cannot uniquely recover an undocumented constitutive branch or reinforcement
transition.

## Remaining admissible recovery actions

1. Request the original MAE 04-03 ZeusNL input deck and `con2` implementation
   or parameter record from the report authors/MAE archive custodian.
2. Request Dolsek and Fajfar's 2005 post-test report and attached OpenSees input
   from the University of Ljubljana/IKPIR archive, using it only for common
   source cross-checks.
3. Request original reinforcement shop drawings or construction drawings from
   the JRC/ELSA SPEAR archive to dimension the bent-up bars.

Until one of these sources is recovered, the unresolved values will not be
inferred by fitting Fig. 2.8.  SPEAR-M0 remains **NOT VALIDATED** and downstream
FVD, optimization, NLTHA/MSA and FEMA P-58 work remains blocked.
