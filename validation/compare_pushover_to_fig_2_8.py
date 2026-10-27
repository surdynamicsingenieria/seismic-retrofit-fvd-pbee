"""Compare OpenSees pushover curves against digitized MAE 04-03 Fig. 2.8."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - plotting is optional for headless audits
    plt = None


ROOT = Path("results/SPEAR/jeong_elnashai")
REF = ROOT / "reference" / "fig_2_8_digitized.csv"
PUSH = ROOT / "pushover"
OUT = ROOT / "comparison"


def read_curve(path: Path, x_name: str, y_name: str) -> list[tuple[float, float]]:
    with path.open() as f:
        rows = csv.DictReader(f)
        return [(float(row[x_name]), float(row[y_name])) for row in rows]


def interp(points: list[tuple[float, float]], x: float) -> float | None:
    pts = sorted(points)
    if x < pts[0][0] or x > pts[-1][0]:
        return None
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y0
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def load_reference() -> dict[str, list[tuple[float, float]]]:
    curves: dict[str, list[tuple[float, float]]] = {}
    with REF.open() as f:
        for row in csv.DictReader(f):
            curves.setdefault(row["curve"], []).append((float(row["top_displacement_mm"]), float(row["base_shear_kN"])))
    return curves


def compare_case(case: str, ref: list[tuple[float, float]]) -> dict[str, float | int | str]:
    sim_path = PUSH / f"{case}.csv"
    sim = read_curve(sim_path, "top_displacement_mm", "base_shear_kN")
    common = []
    for x, y_ref in ref:
        y_sim = interp(sim, x)
        if y_sim is not None:
            common.append((x, abs(y_ref), abs(y_sim)))
    errors = [y_sim - y_ref for _, y_ref, y_sim in common]
    abs_errors = [abs(value) for value in errors]
    ref_peak = max(ref, key=lambda item: abs(item[1]))
    sim_peak = max(sim, key=lambda item: abs(item[1]))
    summary = {
        "case": case,
        "common_points": len(common),
        "reference_peak_kN": abs(ref_peak[1]),
        "reference_peak_disp_mm": ref_peak[0],
        "sim_peak_kN": abs(sim_peak[1]),
        "sim_peak_disp_mm": sim_peak[0],
        "peak_error_pct": 100.0 * (abs(sim_peak[1]) - abs(ref_peak[1])) / abs(ref_peak[1]),
        "mae_kN": sum(abs_errors) / len(abs_errors),
        "rmse_kN": math.sqrt(sum(value * value for value in errors) / len(errors)),
        "max_abs_error_kN": max(abs_errors),
    }
    # Fig. 2.8 digitization does not resolve the origin consistently in all
    # four panels.  Report common 20 and 40 mm secant stiffnesses instead of
    # claiming an origin tangent from pixels that are not present.
    ref_abs = [(abs(x), abs(y)) for x, y in ref]
    sim_abs = [(abs(x), abs(y)) for x, y in sim]
    for displacement_mm in (20.0, 40.0):
        ref_force = interp(ref_abs, displacement_mm)
        sim_force = interp(sim_abs, displacement_mm)
        if ref_force is None or sim_force is None:
            continue
        label = int(displacement_mm)
        summary[f"reference_secant_kN_per_mm_at_{label}mm"] = ref_force / displacement_mm
        summary[f"sim_secant_kN_per_mm_at_{label}mm"] = sim_force / displacement_mm
        summary[f"secant_error_pct_at_{label}mm"] = 100.0 * (sim_force - ref_force) / ref_force
    return summary


def write_plot(reference: dict[str, list[tuple[float, float]]]) -> None:
    if plt is None:
        return

    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.5), sharex=True, sharey=True)
    for ax, case in zip(axes.ravel(), ("xp100", "xn100", "yp100", "yn100")):
        ref = reference[case]
        sim = read_curve(PUSH / f"{case}.csv", "top_displacement_mm", "base_shear_kN")
        ax.plot([x for x, _ in ref], [abs(y) for _, y in ref], label="Fig. 2.8 digitized", lw=2)
        ax.plot([x for x, _ in sim], [abs(y) for _, y in sim], label="OpenSees diagnostic", lw=1.5)
        ax.set_title(case)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("top displacement (mm)")
        ax.set_ylabel("|base shear| (kN)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "fig_2_8_vs_diagnostic_pushover.svg")
    fig.savefig(OUT / "fig_2_8_vs_diagnostic_pushover.png", dpi=180)
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ref = load_reference()
    summaries = [compare_case(case, ref[case]) for case in ("xp100", "xn100", "yp100", "yn100")]
    (OUT / "fig_2_8_comparison_summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    with (OUT / "fig_2_8_comparison_summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summaries)
    write_plot(ref)
    print(json.dumps(summaries, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
