"""Create a compact, auditable table from per-record NLTHA JSON summaries."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def diagnostic_class(status: str, max_drift: float) -> str:
    if status == "COMPLETE":
        return "complete"
    if max_drift >= 0.10:
        return "nonconvergence_drift_ge_10pct_instability_compatible"
    if max_drift >= 0.02:
        return "nonconvergence_drift_2_to_10pct_severe_response"
    return "nonconvergence_drift_lt_2pct_requires_numerical_model_audit"


def main(results_dir: Path) -> None:
    rows = []
    for path in results_dir.glob("RSN*.json"):
        data = json.loads(path.read_text())
        drift = max(data["peak_abs_story_drift_ratio"][axis][i]
                    for axis in ("X", "Y") for i in range(3))
        rows.append({
            "pair_id": data["pair_id"],
            "status": data["status"],
            "diagnostic_class": diagnostic_class(data["status"], drift),
            "completed_steps": data["completed_steps"],
            "requested_steps": data["requested_steps"],
            "completion_fraction": data["completed_steps"] / data["requested_steps"],
            "pga_x_g": data["pga_m_s2"]["X"] / 9.80665,
            "pga_y_g": data["pga_m_s2"]["Y"] / 9.80665,
            "max_abs_drift_ratio": drift,
            "max_abs_roof_x_m": data["peak_abs_roof_displacement_m"]["X"],
            "max_abs_roof_y_m": data["peak_abs_roof_displacement_m"]["Y"],
        })
    rows.sort(key=lambda row: int(row["pair_id"].removeprefix("RSN")))
    with (results_dir / "edp_status_summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    classes = {}
    for row in rows:
        classes[row["diagnostic_class"]] = classes.get(row["diagnostic_class"], 0) + 1
    summary = {"pair_count": len(rows), "class_counts": classes,
               "warning": "Incomplete-case EDPs are last-converged-state diagnostics, not final peaks."}
    (results_dir / "diagnostic_classification.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir", type=Path)
    main(parser.parse_args().results_dir)
