# SPEAR-M0 accepted Section-2 baseline NLTHA

Date: 2026-11-06
Branch: `spear-jeong-elnashai-m0`

## Scope and locked configuration

This campaign establishes the no-FVD nonlinear response-history baseline after
the engineering acceptance of SPEAR-M0. It uses the source-correct Section-2
floor idealization without a rigid diaphragm, the accepted fibre sections and
the non-calibrated `HingeMidpoint` member formulation. The 21 available
FEMA-P695 far-field pairs are applied simultaneously in X and Y at their
unscaled as-recorded intensity. RSN829 is absent and no substitute is used.

Rayleigh damping is 5%, anchored to initial modes 1 and 3. Newmark average
acceleration is used with deterministic Newton, Krylov-Newton, Newton line
search and time-subdivision fallbacks down to 1/16 of the record interval.

## Results

| Outcome | Count | Fraction |
|---|---:|---:|
| Complete histories | 18 | 85.7% |
| Instability-compatible nonconvergence | 3 | 14.3% |
| Moderate-drift numerical stops (<10%) | 0 | 0.0% |

Among complete histories, the median of the pairwise maximum storey drift was
1.586%. The largest complete value was 4.175% for RSN1602.

| Pair | Failure time (s) | Completed fraction | Last-converged max drift | Classification |
|---|---:|---:|---:|---|
| RSN953 | 12.9800 | 43.30% | 46.56% | instability-compatible nonconvergence |
| RSN1158 | 20.9350 | 77.02% | 118.45% | instability-compatible nonconvergence |
| RSN1244 | 43.7775 | 48.64% | 128.56% | instability-compatible nonconvergence |

The three cases were rerun after adding last-state element diagnostics and
reproduced the same classifications. Their largest recorded basic
deformations were 0.568, 1.575 and 1.704, respectively; largest section
deformation-vector components were 12.319, 5.371 and 5.813. These values,
together with the extreme global drifts, distinguish the stops from the prior
low-drift localization pathology. They do not by themselves prove a formal
collapse capacity.

Incomplete-case peaks are truncated last-converged-state diagnostics and must
not be used as final EDPs. The full 22-pair FEMA ensemble must not be claimed
because RSN829 remains unavailable.

## Reproduction

```bash
MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1 \
MPICH_INTERFACE_HOSTNAME=127.0.0.1 \
python models/SPEAR/fvd/run_bidirectional_suite.py \
  models/SPEAR/fvd/manifests/fema_p695_peer_partial_21.json \
  --output-dir results/SPEAR/fvd/baseline_section2_hinge_midpoint_partial21 \
  --suite-label FEMA-P695-partial-21 --damping-ratio 0.05 \
  --member-formulation hinge_midpoint --workers 2 --retry-incomplete

python models/SPEAR/fvd/summarize_bidirectional_suite.py \
  results/SPEAR/fvd/baseline_section2_hinge_midpoint_partial21
```

The licensed PEER waveform bytes remain excluded from Git. The committed
manifest contains their identifiers, units, time steps, scale factors and
SHA-256 hashes. Compact JSON summaries, logs and the aggregate EDP table are
versioned; full CSV histories are intentionally ignored.

## Gate decision

The accepted M0 model has a reproducible 21-pair no-FVD baseline with no
moderate-drift convergence failures. FVD model development and paired
baseline-versus-FVD tests may proceed. Optimization, MSA and FEMA P-58 remain
subject to their separate downstream gates and to explicit propagation of the
documented -Y model-form uncertainty.
