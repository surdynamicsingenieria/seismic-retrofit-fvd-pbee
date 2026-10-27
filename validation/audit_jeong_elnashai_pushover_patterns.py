"""Solver-independent audit of MAE 04-03 Eq. 2.5 / Fig. 2.7 patterns."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "SPEAR" / "jeong_elnashai"
sys.path.insert(0, str(MODEL))

from geometry_source import JOINTS  # noqa: E402
from gravity_mass_source import FLOOR_CM, FLOOR_MASSES_KG  # noqa: E402
from pushover_patterns import REQUIRED_PATTERNS, get_pattern  # noqa: E402

# Direction-specific first-mode vectors are read from the current production
# model at runtime by the nonlinear driver.  Arbitrary positive, nonuniform
# ordinates are sufficient here because this audit verifies the algebra and
# spatial application independently of an eigensolver.
AUDIT_FIRST_MODE = [0.31, 0.68, 1.00]
LOAD_POINTS = {
    "xp100": ("C8", "C9", "C5"),
    "xn100": ("C7", "C4", "C2"),
    "yp100": ("C8", "C6", "C7"),
    "yn100": ("C5", "C1", "C2"),
}


def audit() -> dict:
    result = {"status": "PASS", "cases": {}}
    for case in REQUIRED_PATTERNS:
        rows = get_pattern(case, AUDIT_FIRST_MODE, FLOOR_MASSES_KG)
        dof = case[0]
        sign = -1.0 if case[1] == "n" else 1.0
        total = sum(sum(row) for row in rows)
        if not math.isclose(total, sign, rel_tol=0.0, abs_tol=1e-12):
            raise AssertionError(f"{case}: global normalized resultant {total}")

        floors = []
        for k, (row, cm) in enumerate(zip(rows, FLOOR_CM), start=1):
            floor_resultant = sum(row)
            expected = sign * abs(AUDIT_FIRST_MODE[k - 1]) * FLOOR_MASSES_KG[k - 1]
            denominator = sum(abs(phi) * mass for phi, mass in zip(AUDIT_FIRST_MODE, FLOOR_MASSES_KG))
            expected /= denominator
            if not math.isclose(floor_resultant, expected, rel_tol=0.0, abs_tol=1e-12):
                raise AssertionError(f"{case} floor {k}: Eq. 2.5 mismatch")

            mz = 0.0
            for point, force in zip(LOAD_POINTS[case], row):
                x, y = JOINTS[point]
                if dof == "x":
                    mz -= (y - cm[1]) * force
                else:
                    mz += (x - cm[0]) * force
            floors.append({
                "floor": k,
                "normalized_resultant": floor_resultant,
                "normalized_torque_about_cm": mz,
            })
        if any(math.isclose(item["normalized_torque_about_cm"], 0.0, abs_tol=1e-12) for item in floors):
            raise AssertionError(f"{case}: Fig. 2.7 torque was lost")
        result["cases"][case] = {"global_resultant": total, "floors": floors}

    out = ROOT / "results" / "SPEAR" / "jeong_elnashai" / "pushover_pattern_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
