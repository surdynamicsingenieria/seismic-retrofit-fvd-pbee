# SPEAR-M0 NLTHA convergence audit — 2026-11-02

## Scope

This audit investigates RSN 900 and 1633, which stopped in the unscaled
partial-21 suite while centre-of-mass storey drifts remained below 2%. No
material, mass, damping, record or scale parameter was calibrated.

## Directional isolation

| Case | Result | Last step | Requested | Max CM drift |
|---|---|---:|---:|---:|
| RSN 900 X | incomplete | 825 | 2199 | 1.180% |
| RSN 900 Y | complete | 2199 | 2199 | 0.367% |
| RSN 1633 X | incomplete | 598 | 2675 | 1.287% |
| RSN 1633 Y | incomplete | 533 | 2299 | 1.193% |

RSN 900 is therefore localized to X response. RSN 1633 fails independently in
both directions; torsional X-Y coupling is not required to trigger either
failure.

## Solver sensitivity

Replacing `NormDispIncr` by `EnergyIncr` produced the same stopping steps for
all three incomplete directional cases. Newton, Krylov-Newton, Newton line
search and recursive time subdivision through 1/16 of the input interval also
failed. The stops cannot be attributed only to the selected convergence test
or original record step.

## Last-committed-state localization

Generic element basic and section deformations were scanned after the failed
interval. The largest responses are:

| Case | Controlling location | Element | Largest section component |
|---|---|---:|---:|
| RSN 900 X | C4, storey 1, base segment | 21 | 24.086 1/m; axial strain -1.055 |
| RSN 1633 X | C2, storey 3, end segment | 108 | 0.207 1/m |
| RSN 1633 Y | C8, storey 1, top segment | 4 | 2.791 1/m |
| RSN 1633 Y | B5, floor 2, end segment | 120043 | 2.375 1/m |

These local values are incompatible with interpreting the sub-2% CM drift as
a regular moderate response. They show extreme localization/pathological
section states in the current displacement-based, two-point fibre
discretization. They do not by themselves identify whether the root cause is
the zero-tension `Concrete02` mapping, section integration, member mesh,
P-Delta interaction, or a combination.

## Decision

The current model remains useful for the accepted modal/pushover engineering
benchmark and for NLTHA infrastructure verification, but it is **not yet
accepted for production NLTHA, FVD comparison, fragility or PBEE inference**.
The next admissible work is controlled formulation sensitivity: force-based
versus displacement-based elements, integration order/mesh objectivity,
P-Delta diagnostic isolation, and source-backed concrete tensile behavior.
No variant may be selected merely because it converges.
