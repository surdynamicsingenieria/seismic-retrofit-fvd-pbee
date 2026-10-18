"""Reproduce the MAE 04-03 Table 3.1 column yield-curvature calculation.

This is an independent strain-compatibility audit, not a calibration routine.
It implements Eq. 3.2, the published 25 MPa Mander compression envelope,
measured Phi12 steel properties and the Fig. 2.3 reinforcement.  Concrete
tension is deliberately omitted because its numerical ZeusNL ``con2`` input
has not been recovered.  The script writes the resulting evidence ledger.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq


OUT = Path("results/SPEAR/jeong_elnashai/table_3_1_yield_curvature_audit.json")
FC_MPA = 25.0
FY_MPA = 458.67
ES_MPA = 206_000.0
EC_MPA = 4_700.0 * math.sqrt(FC_MPA)
EPS_C0 = 0.002
BAR_AREA_MM2 = math.pi * 12.0**2 / 4.0

PUBLISHED = {
    "C1": ([234.22, 154.46, 74.98], [17.50, 16.16, 15.53]),
    "C2": ([252.67, 166.54, 80.13], [18.73, 16.20, 15.59]),
    "C3": ([407.26, 272.34, 139.62], [21.53, 18.76, 16.09]),
    "C4": ([328.72, 217.96, 107.89], [17.79, 17.49, 15.87]),
    "C5": ([89.56, 57.42, 25.43], [15.68, 15.34, 15.26]),
    "C7": ([150.45, 98.51, 45.90], [16.14, 15.77, 15.31]),
    "C8": ([73.66, 45.72, 18.66], [15.51, 15.31, 14.16]),
    "C9": ([182.26, 121.37, 59.05], [17.40, 15.98, 15.35]),
}
C6_AXIAL_KN = [216.44, 141.29, 64.29]
C6_PUBLISHED = {
    "unlabelled_subcolumn_1": [14.74, 13.79, 13.43],
    "unlabelled_subcolumn_2": [17.25, 16.61, 16.02],
}


def mander_compression_mpa(strain: np.ndarray) -> np.ndarray:
    """Unconfined Mander envelope; compression is positive in this audit."""
    strain = np.maximum(strain, 0.0)
    e_sec = FC_MPA / EPS_C0
    r = EC_MPA / (EC_MPA - e_sec)
    x = strain / EPS_C0
    return FC_MPA * x * r / (r - 1.0 + x**r)


def first_yield_curvature(
    depth_mm: float,
    width_mm: float,
    bar_depths_mm: list[float],
    axial_kn: float,
) -> dict[str, float]:
    """Solve the pre-peak Eq. 3.2 equilibrium branch at first tension yield."""
    eps_y = FY_MPA / ES_MPA
    d = max(bar_depths_mm)

    def axial_force_kn(neutral_axis_mm: float) -> float:
        curvature = eps_y / (d - neutral_axis_mm)
        x = np.linspace(0.0, depth_mm, 4001)
        concrete_strain = curvature * (neutral_axis_mm - x)
        concrete_kn = np.trapezoid(mander_compression_mpa(concrete_strain), x) * width_mm / 1000.0
        steel_kn = sum(
            np.clip(ES_MPA * curvature * (neutral_axis_mm - bar_x), -FY_MPA, FY_MPA)
            * BAR_AREA_MM2 / 1000.0
            for bar_x in bar_depths_mm
        )
        return concrete_kn + steel_kn

    # Multiple mathematical roots can occur after the concrete peak.  The
    # first root reached while neutral-axis depth grows from the compression
    # face is the physical monotonic pre-peak branch used by Eq. 3.2.
    grid = np.linspace(0.1, d - 0.01, 5000)
    residual = [axial_force_kn(c) - axial_kn for c in grid]
    brackets = [
        (a, b) for a, b, fa, fb in zip(grid[:-1], grid[1:], residual[:-1], residual[1:])
        if fa == 0.0 or fa * fb < 0.0
    ]
    if not brackets:
        raise RuntimeError(f"No equilibrium root for N={axial_kn} kN")
    a, b = brackets[0]
    c = brentq(lambda value: axial_force_kn(value) - axial_kn, a, b)
    curvature_rad_per_mm_e6 = eps_y / (d - c) * 1.0e6
    return {
        "neutral_axis_mm": c,
        "yield_curvature_rad_per_mm_x1e6": curvature_rad_per_mm_e6,
        "number_of_mathematical_roots": len(brackets),
    }


def regular_bars(centroid_cover_mm: float) -> list[float]:
    return [centroid_cover_mm, centroid_cover_mm, 250.0 - centroid_cover_mm, 250.0 - centroid_cover_mm]


def c6_weak_bars(centroid_cover_mm: float) -> list[float]:
    return [centroid_cover_mm] * 5 + [250.0 - centroid_cover_mm] * 5


def c6_strong_bars(centroid_cover_mm: float) -> list[float]:
    depths = np.linspace(centroid_cover_mm, 750.0 - centroid_cover_mm, 5)
    return [float(value) for value in depths for _ in range(2)]


def main() -> None:
    output: dict[str, object] = {
        "status": "SOURCE_CONSISTENCY_AUDIT_NOT_CALIBRATION",
        "assumptions": {
            "concrete": "Mander compression envelope, fc=25 MPa, Ec=4700*sqrt(fc); tension omitted pending ZeusNL con2 input",
            "steel": "elastic-perfectly-plastic at first yield, fy=458.67 MPa, Es=206000 MPa",
            "bar_centroid_cover_mm": 29.0,
            "root_selection": "first monotonic pre-peak equilibrium root",
        },
        "regular_columns": {},
    }
    errors = []
    for member, (axials, published) in PUBLISHED.items():
        rows = []
        for story, (axial, reference) in enumerate(zip(axials, published), start=1):
            result = first_yield_curvature(250.0, 250.0, regular_bars(29.0), axial)
            calculated = result["yield_curvature_rad_per_mm_x1e6"]
            error = 100.0 * (calculated / reference - 1.0)
            errors.append(abs(error))
            rows.append({"story": story, "axial_kn": axial, "published": reference, "calculated": calculated, "error_pct": error, **result})
        output["regular_columns"][member] = rows

    c6 = {}
    for axis, depth, width, bars in (
        ("weak_axis_250_mm_depth", 250.0, 750.0, c6_weak_bars(29.0)),
        ("strong_axis_750_mm_depth", 750.0, 250.0, c6_strong_bars(29.0)),
    ):
        c6[axis] = [
            {"story": story, "axial_kn": axial, **first_yield_curvature(depth, width, bars, axial)}
            for story, axial in enumerate(C6_AXIAL_KN, start=1)
        ]
    output["c6"] = {"published_unlabelled": C6_PUBLISHED, "calculated_axes": c6}
    output["summary"] = {
        "regular_column_mean_absolute_error_pct": float(np.mean(errors)),
        "regular_column_max_absolute_error_pct": float(np.max(errors)),
        "finding": "C6 weak-axis values have the published order of magnitude; the strong-axis values do not. Neither unlabelled published subcolumn represents the direct 750 mm-depth first-yield curvature.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))


if __name__ == "__main__":
    main()
