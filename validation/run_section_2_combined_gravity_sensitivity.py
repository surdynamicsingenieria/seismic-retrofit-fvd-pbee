"""Combined Section 2 no-diaphragm and reconstructed Fig. 2.6 gravity sensitivity."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "SPEAR" / "jeong_elnashai"
sys.path.insert(0, str(MODEL_DIR))
sys.path.insert(0, str(ROOT / "validation"))

import spear_m0_jeong_elnashai_nonlinear as model  # noqa: E402
from run_fig_2_6_beam_gravity_sensitivity import gravity_on_beams  # noqa: E402

OUT = ROOT / "results" / "SPEAR" / "jeong_elnashai" / "sensitivity" / "section_2_combined_gravity"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="*", default=["xp100", "xn100", "yp100", "yn100"])
    parser.add_argument("--target-mm", type=float, default=100.0)
    parser.add_argument("--du-mm", type=float, default=1.0)
    args = parser.parse_args()
    old_flag, old_gravity, old_model_out = model.RIGID_DIAPHRAGM, model.gravity, model.OUT
    # gravity_on_beams writes its balance ledger through its own module-level OUT.
    model.RIGID_DIAPHRAGM = False
    model.gravity = gravity_on_beams
    model.OUT = OUT / "pushover"
    model.OUT.mkdir(parents=True, exist_ok=True)
    try:
        return max(model.run(case, target_mm=args.target_mm, du_mm=args.du_mm) for case in args.cases)
    finally:
        model.RIGID_DIAPHRAGM, model.gravity, model.OUT = old_flag, old_gravity, old_model_out


if __name__ == "__main__":
    raise SystemExit(main())
