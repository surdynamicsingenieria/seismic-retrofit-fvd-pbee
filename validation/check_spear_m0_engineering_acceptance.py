"""Engineering acceptance gate for the frozen SPEAR-M0 baseline.

This gate checks global benchmark fidelity required for subsequent retrofit
studies.  It does not claim line-by-line reproduction of the unavailable
UIUC/ZeusNL input deck or pointwise reproduction of MAE 04-03 Fig. 2.8.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

ROOT = Path("results/SPEAR/jeong_elnashai")
MODAL_LIMIT_PCT = 10.0
PEAK_LIMIT_PCT = 15.0

modal = json.loads((ROOT / "modal_baseline.json").read_text())
curves = json.loads((ROOT / "comparison/fig_2_8_comparison_summary.json").read_text())
patterns = json.loads((ROOT / "pushover_pattern_audit.json").read_text())
model_root = Path("models/SPEAR/jeong_elnashai")
lock = json.loads((model_root / "SPEAR_M0_BASELINE_LOCK.json").read_text())
hash_checks = {
    name: hashlib.sha256((model_root / name).read_bytes()).hexdigest() == expected
    for name, expected in lock["files_sha256"].items()
}

modal_checks = [abs(value) <= MODAL_LIMIT_PCT for value in modal["errors_pct"]]
peak_checks = {row["case"]: abs(row["peak_error_pct"]) <= PEAK_LIMIT_PCT for row in curves}
peaks = {row["case"]: row["sim_peak_kN"] for row in curves}
qualitative = {
    "yn_stronger_than_yp": peaks["yn100"] > peaks["yp100"],
    "mean_y_stronger_than_mean_x": (peaks["yp100"] + peaks["yn100"]) > (peaks["xp100"] + peaks["xn100"]),
    "four_spatial_patterns_pass": patterns["status"] == "PASS" and len(patterns["cases"]) == 4,
}

passed = (all(modal_checks) and all(peak_checks.values())
          and all(qualitative.values()) and all(hash_checks.values()))
result = {
    "status": "PASS" if passed else "FAIL",
    "scope": "engineering benchmark validation for FVD/PBEE research",
    "limitations": [
        "not an exact reconstruction of the unavailable UIUC ZeusNL input deck",
        "Fig. 2.8 pointwise curve shape and post-peak response are not acceptance gates",
        "pre-peak secant stiffness is overestimated by approximately 18-27 percent",
    ],
    "criteria": {
        "modal_period_absolute_error_limit_pct": MODAL_LIMIT_PCT,
        "pushover_peak_absolute_error_limit_pct": PEAK_LIMIT_PCT,
        "qualitative_response_checks_required": True,
    },
    "modal": {
        "targets_s": modal["targets_s"],
        "model_s": modal["periods_s"],
        "errors_pct": modal["errors_pct"],
        "checks": modal_checks,
    },
    "pushover_peak_checks": peak_checks,
    "qualitative_checks": qualitative,
    "baseline_file_hash_checks": hash_checks,
    "downstream_authorization": "FVD model development and baseline NLTHA authorized" if passed else "blocked",
}

out = ROOT / "engineering_acceptance.json"
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
raise SystemExit(0 if passed else 2)
