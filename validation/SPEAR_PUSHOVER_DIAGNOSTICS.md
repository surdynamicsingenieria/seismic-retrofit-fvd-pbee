# SPEAR nonlinear pushover diagnostics

Status: **DIAGNOSTIC ONLY — NOT YET VALIDATED**

Frozen modal model remains unchanged. These runs use the current nonlinear
reconstruction and are retained to guide completion of the exact B13/B14
topology and nonlinear member mapping.

## +X diagnostic

Current principal EFCP-oriented nonlinear model:

- roof displacement reached: 0.18334 m
- peak base shear: 420.68 kN
- termination: nonconvergence before 0.20 m target
- initial nonlinear-model periods: 0.54658 / 0.48763 / 0.37671 s

This is not accepted as the final +X validation curve.

## +Y diagnostic

Correct modal-participation selection was used.

Modal participation:
- Mode 1: X 76.55%, Y 4.29%, Rz 8.64%
- Mode 2: X 7.89%, **Y 72.25%**, Rz 4.75%
- Mode 3: X 4.93%, Y 6.91%, **Rz 76.14%**

Selected lateral pattern: **Mode 2**.

Results:
- roof displacement reached: 0.20031 m
- peak base shear: 433.37 kN
- status: numerical run completed to target
- initial nonlinear-model periods: 0.54658 / 0.48763 / 0.37671 s

## Interpretation

The +Y run is numerically stable to 0.20 m, but it is still diagnostic.
The B13/B14 nonlinear topology and published member subdivision must be
reconciled before either +X or +Y is marked as physically validated.

No FVD, optimization, NLTHA/MSA, or FEMA P-58 work is authorized from these
diagnostic curves.
