"""Reproduce the MAE 04-03 Section 2 no-diaphragm idealization.

This is a source-bounded sensitivity, not an accepted production change.
Section 2.2.2 says slabs are omitted.  Section 5.2 states explicitly that the
rigid diaphragm was introduced later as a refined model.  Roof displacement is
controlled at C3, consistent with the report's stated response location.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "SPEAR" / "jeong_elnashai"
sys.path.insert(0, str(MODEL_DIR))

import spear_m0_jeong_elnashai_nonlinear as model  # noqa: E402

OUT = ROOT / "results" / "SPEAR" / "jeong_elnashai" / "sensitivity" / "section_2_no_diaphragm"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="*", default=["xp100", "xn100", "yp100", "yn100"])
    parser.add_argument("--target-mm", type=float, default=200.0)
    parser.add_argument("--du-mm", type=float, default=0.5)
    args = parser.parse_args()
    old_flag, old_out = model.RIGID_DIAPHRAGM, model.OUT
    model.RIGID_DIAPHRAGM = False
    model.OUT = OUT / "pushover"
    model.OUT.mkdir(parents=True, exist_ok=True)
    try:
        return max(model.run(case, target_mm=args.target_mm, du_mm=args.du_mm) for case in args.cases)
    finally:
        model.RIGID_DIAPHRAGM, model.OUT = old_flag, old_out


if __name__ == "__main__":
    raise SystemExit(main())
