# SPEAR FVD/NLTHA infrastructure

This directory extends the locked SPEAR-M0 engineering baseline without
modifying its structural source files.

Implemented:

- explicit ground-motion units (`g`, `m/s2`, `cm/s2`) and scale factors;
- baseline nonlinear response-history driver;
- explicit Rayleigh damping ratio and modal pair;
- nonlinear viscous law `F=C|v|^alpha sign(v)` through OpenSees `Viscous`;
- validation of FVD tags, nodes, coefficient and exponent.

No record, damping ratio, FVD placement, coefficient `C` or exponent `alpha`
is selected by default. Those are research design variables and must be stored
in a separate versioned configuration before comparative analyses.

Example baseline invocation:

```bash
MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1 python \
  models/SPEAR/fvd/run_baseline_nltha.py RECORD.txt \
  --record-dt 0.01 --record-unit g --scale 1.0 --direction 1 \
  --damping-ratio 0.02 --output results/SPEAR/nltha/m0/record_x.csv
```

The next gate is selection and provenance documentation of the ground-motion
set, followed by a baseline M0 NLTHA convergence and energy-balance campaign.
