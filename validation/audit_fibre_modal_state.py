"""Audit SPEAR fibre-model periods before and after the gravity state."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

MODEL_DIR = Path("models/SPEAR/jeong_elnashai")
sys.path.insert(0, str(MODEL_DIR))

import spear_m0_jeong_elnashai_nonlinear as model  # noqa: E402
import spear_m0_jeong_elnashai as elastic_model  # noqa: E402


OUT = Path("results/SPEAR/jeong_elnashai/modal_fibre_state_audit.json")
TARGET = [0.51, 0.46, 0.40, 0.18]


def periods() -> list[float]:
    values = model.ops.eigen("-fullGenLapack", 4)
    return [2.0 * math.pi / math.sqrt(value) for value in values]


def errors(values: list[float], reference: list[float]) -> list[float]:
    return [100.0 * (value - ref) / ref for value, ref in zip(values, reference)]


def main() -> int:
    # Rebuild the current source-ledger elastic model.  Do not retain a copied
    # period vector here: geometry/mass corrections must propagate into this
    # comparison automatically.
    elastic_model.build()
    elastic_baseline = periods()
    model.ops.wipe()

    names, nt, _masters = model.build()
    pre = periods()
    gravity_exit_code = model.gravity(names, nt)
    post = periods()
    result = {
        "status": "DIAGNOSTIC_ONLY",
        "published_periods_s": TARGET,
        "elastic_baseline_periods_s": elastic_baseline,
        "fibre_pre_gravity_periods_s": pre,
        "fibre_post_gravity_periods_s": post,
        "pre_vs_published_error_pct": errors(pre, TARGET),
        "post_vs_published_error_pct": errors(post, TARGET),
        "pre_vs_elastic_baseline_error_pct": errors(pre, elastic_baseline),
        "gravity_period_shift_pct": errors(post, pre),
        "gravity_exit_code": gravity_exit_code,
        "interpretation": (
            "The fibre model does not reproduce the elastic baseline exactly, "
            "and gravity causes an additional material/geometric tangent-stiffness shift."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    model.ops.wipe()
    return 0 if gravity_exit_code == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
