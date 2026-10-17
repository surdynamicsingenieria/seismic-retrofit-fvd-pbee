# SPEAR mass-source audit - 2026-10-15

## Finding

The repository currently uses:

| Floor | Mass (t) | CM x (m) | CM y (m) | Polar mass (tm2) |
|---:|---:|---:|---:|---:|
| 1 | 65.5 | 4.53 | 5.29 | 1254 |
| 2 | 65.5 | 4.53 | 5.29 | 1254 |
| Roof | 64.1 | 4.57 | 5.33 | 1196 |

These exact values were traced to Aurel Stratan and Peter Fajfar, *Seismic
Assessment of the SPEAR Test Structure*. They describe the Ljubljana partner
model and cannot be silently treated as the Jeong-Elnashai/UIUC ZeusNL mass
input.

MAE 04-03 specifies the Jeong-Elnashai mass construction rule:

- dead load plus 30% live load;
- slab and slab load distributed to the nearest beams per Fig. 2.6;
- mass obtained using 9.807 m/s2;
- masses placed at beam-column connections;
- total building weight reported as 1957 kN.

The current floor masses total 195.1 t or 1913.35 kN. The reported MAE total is
equivalent to 199.55 t. Thus the current diagnostic mass is 4.45 t (-2.23%)
below the Jeong-Elnashai total before considering the unresolved nodal spatial
distribution.

## Decision

The current tuples are retained only to keep the diagnostic model executable.
They are explicitly prohibited for validation acceptance. Values from other
partner models (including later publications with different floor masses) will
not be substituted. Acceptance requires either the original ZeusNL nodal mass
input or a fully reproducible Fig. 2.6 load-to-node ledger that closes to the
1957 kN total.

## Sources

- Jeong and Elnashai, MAE Report 04-03, Sections 2.2.4 and 2.3.2.
- Stratan and Fajfar, *Seismic Assessment of the SPEAR Test Structure*.
