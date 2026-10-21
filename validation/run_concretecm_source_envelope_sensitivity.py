"""Source-constrained ZEUS-NL con2 / ConcreteCM sensitivity.

This diagnostic does not replace the production material. It maps the published
MAE 04-03 compression constraints to a continuous ConcreteCM envelope and keeps
concrete tension equal to zero because the SPEAR con2 tensile input is not
published. Results are written to a separate sensitivity directory.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

MODEL_DIR = Path("models/SPEAR/jeong_elnashai")
sys.path.insert(0, str(MODEL_DIR))

import spear_m0_jeong_elnashai_nonlinear as model  # noqa: E402

FPCC = -25.25e6
EPCC = -0.0021
EC = 23.5e9
RC = 1.3321247029575265
XCRN = 100.0
OUT = Path("results/SPEAR/jeong_elnashai/sensitivity/concretecm_zero_tension")


def install_source_envelope() -> None:
    original = model.ops.uniaxialMaterial

    def material(kind, tag, *args):
        if kind == "Concrete02" and tag == 1:
            return original(
                "ConcreteCM",
                tag,
                FPCC,
                EPCC,
                EC,
                RC,
                XCRN,
                0.0,
                1.0e-6,
                1.2,
                1.0,
            )
        return original(kind, tag, *args)

    model.ops.uniaxialMaterial = material


def periods() -> list[float]:
    values = model.ops.eigen("-fullGenLapack", 4)
    return [2.0 * math.pi / math.sqrt(value) for value in values]


def modal_audit() -> dict:
    names, nt, _masters = model.build()
    pre = periods()
    gravity_exit_code = model.gravity(names, nt)
    post = periods()
    result = {
        "status": "SENSITIVITY_ONLY_NOT_ACCEPTED",
        "material": "ConcreteCM continuous compression envelope; zero tension",
        "fpcc_Pa": FPCC,
        "epcc": EPCC,
        "Ec_Pa": EC,
        "rc_from_MAE_0.85_point": RC,
        "xcrn_non_active": XCRN,
        "pre_gravity_periods_s": pre,
        "post_gravity_periods_s": post,
        "gravity_exit_code": gravity_exit_code,
        "blocker": "The numerical SPEAR ZeusNL con2 tensile strength remains unrecovered.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "modal.json").write_text(json.dumps(result, indent=2) + "\n")
    model.ops.wipe()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "cases",
        nargs="*",
        choices=("xp100", "xn100", "yp100", "yn100"),
        default=["xp100"],
    )
    args = parser.parse_args()
    install_source_envelope()
    print(json.dumps(modal_audit(), indent=2))
    model.OUT = OUT / "pushover"
    model.OUT.mkdir(parents=True, exist_ok=True)
    codes = {case: model.run(case) for case in args.cases}
    return 0 if all(code == 0 for code in codes.values()) else 3


if __name__ == "__main__":
    raise SystemExit(main())
