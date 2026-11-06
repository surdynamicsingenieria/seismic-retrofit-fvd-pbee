"""Source-bounded 45-degree bent-bar transition sensitivity for SPEAR Section 2."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "SPEAR" / "jeong_elnashai"
sys.path.insert(0, str(MODEL_DIR))

import spear_m0_jeong_elnashai_nonlinear as model  # noqa: E402
from reinforcement_source import BAR_DIAMETER_M, COVER_M  # noqa: E402

OUT = ROOT / "results" / "SPEAR" / "jeong_elnashai" / "sensitivity" / "section_2_bent_bar_45deg"


def main() -> int:
    model.RIGID_DIAPHRAGM = False
    depth = 0.50
    centroid_cover = COVER_M + BAR_DIAMETER_M["phi8"] + BAR_DIAMETER_M["phi12"] / 2.0
    vertical_separation = depth - 2.0 * centroid_cover
    transition_m = vertical_separation  # horizontal projection at 45 degrees
    push = OUT / "pushover"
    push.mkdir(parents=True, exist_ok=True)
    audit = {
        "status": "SENSITIVITY_ONLY_NOT_ACCEPTED",
        "source_inclination_deg": 45.0,
        "beam_depth_m": depth,
        "longitudinal_bar_centroid_cover_m": centroid_cover,
        "vertical_bar_row_separation_m": vertical_separation,
        "beam_hinge_length_m": transition_m,
        "note": "Abrupt section transition is only a proxy for the undimensioned bent-bar zone.",
    }
    (OUT / "input_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    codes = {
        case: model.run(case, target_mm=200.0, du_mm=0.5,
                        member_formulation="hinge_midpoint", output_dir=push,
                        beam_hinge_length_m=transition_m)
        for case in ("xp100", "xn100", "yp100", "yn100")
    }
    print(json.dumps({"input": audit, "exit_codes": codes}, indent=2))
    return 0 if all(code == 0 for code in codes.values()) else 3


if __name__ == "__main__":
    raise SystemExit(main())
