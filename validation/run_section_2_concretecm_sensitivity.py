"""Section 2 no-diaphragm sensitivity to the published concrete envelope.

This is not a production material calibration.  It combines the source-bounded
ConcreteCM compression envelope with the regularized member formulation and
keeps concrete tension at zero because the SPEAR-specific ZeusNL input is not
available.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "SPEAR" / "jeong_elnashai"
sys.path.insert(0, str(MODEL_DIR))
sys.path.insert(0, str(ROOT / "validation"))

import spear_m0_jeong_elnashai_nonlinear as model  # noqa: E402
from run_concretecm_source_envelope_sensitivity import install_source_envelope  # noqa: E402

OUT = ROOT / "results" / "SPEAR" / "jeong_elnashai" / "sensitivity" / "section_2_concretecm_hinge_midpoint"
CASES = ("xp100", "xn100", "yp100", "yn100")


def periods() -> list[float]:
    values = model.ops.eigen("-fullGenLapack", 4)
    return [2.0 * math.pi / math.sqrt(value) for value in values]


def main() -> int:
    install_source_envelope()
    model.RIGID_DIAPHRAGM = False

    names, nt, _masters = model.build(member_formulation="hinge_midpoint")
    pre = periods()
    gravity_exit_code = model.gravity(names, nt)
    post = periods()
    model.ops.wipe()

    OUT.mkdir(parents=True, exist_ok=True)
    audit = {
        "status": "SENSITIVITY_ONLY_NOT_ACCEPTED",
        "rigid_diaphragm": False,
        "member_formulation": "hinge_midpoint",
        "material": "published-point ConcreteCM compression envelope; zero tension",
        "pre_gravity_periods_s": pre,
        "post_gravity_periods_s": post,
        "gravity_exit_code": gravity_exit_code,
        "blocker": "Exact ZeusNL con2 law and SPEAR-specific input remain unavailable.",
    }
    (OUT / "modal.json").write_text(json.dumps(audit, indent=2) + "\n")

    push = OUT / "pushover"
    push.mkdir(parents=True, exist_ok=True)
    codes = {
        case: model.run(case, target_mm=200.0, du_mm=0.5,
                        member_formulation="hinge_midpoint", output_dir=push)
        for case in CASES
    }
    print(json.dumps({"modal": audit, "exit_codes": codes}, indent=2))
    return 0 if all(code == 0 for code in codes.values()) else 3


if __name__ == "__main__":
    raise SystemExit(main())
