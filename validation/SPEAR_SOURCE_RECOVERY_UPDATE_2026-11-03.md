# SPEAR source-recovery update — 2026-11-03

## Scope

This pass followed two explicit public leads for missing SPEAR inputs. It did
not transfer parameters from a different analytical model into the UIUC
ZEUS-NL reconstruction.

## Ljubljana post-test OpenSees package

Azarbakht, Ghafory-Ashtiany and Dolšek (1ECEES, 2006) state that the input
files of the SPEAR mathematical model were available at
`www.ikpir.com/projects/spear`. The OpenSees user forum later linked the exact
package name:

`http://maringrubisic.com/OpenSees/SPEAR-Post-Test-Model.zip`

The live package now returns HTTP 404. A Wayback CDX inventory of the complete
IKPIR SPEAR path contains only two successful archived resources: the project
path itself and `SPEARinternationalWorkshopPaper.pdf`. The archived project
path is an application error page, and no ZIP/Tcl resource is preserved. A
second CDX lookup for the exact `SPEAR-Post-Test-Model.zip` URL returns an empty
capture set. GitHub global code search found no copy under the exact package
name, workshop filename, or historical IKPIR path.

This package would have been a cross-check source only. The Ljubljana model is
a concentrated-plasticity post-test model and is not the target Jeong--Elnashai
distributed-fibre ZEUS-NL model.

## Bent reinforcement geometry

Negro et al. (13WCEE paper 3304) independently describe the beam reinforcement
as 12 mm and 20 mm straight and bent bars, with the bent bars inclined at 45
degrees. This recovers the inclination but not the longitudinal coordinates at
which each bar leaves and rejoins the top/bottom layers. The cited primary
design report is:

M.N. Fardis (2002), *Design of an Irregular Building for the SPEAR Project -
Description of the 3-Storey Structure*, University of Patras.

The report is discoverable as a bibliographic reference but no public report
file or construction drawing was recovered. Therefore a 45-degree line can be
enforced in a future reconstruction only after at least one bend endpoint is
known; selecting that endpoint from the pushover response would be calibration.

## Source URLs checked

- IKPIR workshop paper: <https://ikpir.com/projects/spear/SPEARinternationalWorkshopPaper.pdf>
- OpenSees forum package reference: <https://opensees.ist.berkeley.edu/community/viewtopic.php?p=103901>
- 13WCEE paper 3304: <https://www.iitk.ac.in/nicee/wcee/article/13_3304.pdf>
- Fardis report bibliographic reference: <https://opencivilengineeringjournal.com/VOLUME/11/PAGE/1158/>

## Result

The missing-data statement is narrowed:

- recovered: bent-bar inclination = 45 degrees;
- not recovered: bend start/end coordinates and complete bar-by-bar layout;
- not recovered: Ljubljana `SPEAR-Post-Test-Model.zip`;
- not recovered: UIUC ZEUS-NL SPEAR input deck or SPEAR-specific `con2` input.

No production model parameter changes are justified by this recovery pass.
