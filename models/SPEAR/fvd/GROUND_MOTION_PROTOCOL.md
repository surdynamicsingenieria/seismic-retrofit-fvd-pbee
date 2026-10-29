# Ground-motion protocol

## Phase A — software verification

Synthetic zero and 0.05 g sinusoidal fixtures are used only to verify units,
time integration, convergence and EDP extraction. They are prohibited for
structural conclusions.

## Phase B — comparative M0/FVD development

Use the 22 bidirectional far-field record pairs defined by FEMA P-695. This is
a fixed ensemble of recorded motions suitable for consistent comparative and
collapse-oriented studies. Both components must be retained as a pair, with
event, station, time step, units, original filename and SHA-256 recorded in the
suite manifest.

Primary references:

- FEMA P-695, Appendix A: https://nehrpsearch.nist.gov/static/files/FEMA/fema_p695.pdf
- FEMA P-1026 description of the 22-pair ensemble:
  https://www.fema.gov/sites/default/files/documents/fema-p-1026.pdf
- PEER NGA database provenance: https://peer.berkeley.edu/research/nga-west-2

The Phase B suite is intended to compare M0 and FVD alternatives and support
IDA methodology development. It is not a substitute for a site-specific PBEE
hazard definition.

## Phase C — site-specific PBEE

Before loss or annualized-risk calculations, define the project site, hazard
levels, target spectra, soil class, component combination and scaling limits.
Select records from a verified database against those targets. This phase
remains a separate gate because no project site/hazard has yet been fixed.

## Mandatory manifest fields

Every component must include record ID, event, station, component, local path,
time step, acceleration unit, scale factor, source URL and SHA-256. Analyses
must fail before model construction if a file, unit or digest is invalid.
