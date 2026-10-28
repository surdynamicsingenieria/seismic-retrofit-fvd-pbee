"""Compare the Section 2 no-diaphragm sensitivity with MAE Fig. 2.8."""
import csv
import json
import argparse
from pathlib import Path

ROOT = Path("results/SPEAR/jeong_elnashai")
parser = argparse.ArgumentParser()
parser.add_argument("--sensitivity", default="section_2_no_diaphragm")
args = parser.parse_args()
SENS = ROOT / "sensitivity" / args.sensitivity


def read(path, curve=None):
    rows = []
    for row in csv.DictReader(path.open()):
        if curve is None or row.get("curve") == curve:
            rows.append((abs(float(row["top_displacement_mm"])), abs(float(row["base_shear_kN"]))))
    return sorted(rows)


def interp(points, x):
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


rows = []
for case in ("xp100", "xn100", "yp100", "yn100"):
    ref = read(ROOT / "reference/fig_2_8_digitized.csv", case)
    sim = read(SENS / f"pushover/{case}.csv")
    ref_peak = max(ref, key=lambda p: p[1])
    sim_peak = max(sim, key=lambda p: p[1])
    row = {"case": case, "reference_peak_kN": ref_peak[1], "sim_peak_kN": sim_peak[1],
           "peak_error_pct": 100 * (sim_peak[1] - ref_peak[1]) / ref_peak[1],
           "reached_mm": sim[-1][0]}
    for x in (20, 40):
        yr, ys = interp(ref, x), interp(sim, x)
        row[f"secant_error_pct_at_{x}mm"] = 100 * (ys - yr) / yr
    rows.append(row)

SENS.mkdir(parents=True, exist_ok=True)
(SENS / "comparison_summary.json").write_text(json.dumps(rows, indent=2) + "\n")
print(json.dumps(rows, indent=2))
