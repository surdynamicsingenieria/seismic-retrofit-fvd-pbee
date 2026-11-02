# SPEAR-M0 unscaled PEER partial-21 NLTHA

This directory reports simultaneous bidirectional analyses of the 21 available
FEMA P-695 far-field pairs. RSN 829 is absent and no substitute was used.

The motions are unscaled, processed and as-recorded. Damping is 5% Rayleigh
damping anchored to pre-gravity modes 1 and 3. Thirteen analyses completed all
requested steps. Eight stopped after deterministic Newton, Krylov-Newton,
line-search and adaptive time subdivision through 1/16 of the record interval.

The diagnostic classification is intentionally not a collapse declaration:

- drift >=10% at the last converged state: instability-compatible;
- drift 2--10%: severe-response nonconvergence;
- drift <2%: numerical/model audit required.

EDPs for incomplete cases describe only the last converged history and are not
final response peaks. Full time-history CSV files are locally retained and
ignored by Git because they are large and reproducible from the licensed PEER
inputs. Per-case JSON summaries, logs and compact suite tables are versioned.
