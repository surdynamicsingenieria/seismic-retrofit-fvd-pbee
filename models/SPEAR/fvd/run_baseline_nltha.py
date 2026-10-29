"""Baseline NLTHA driver for the frozen SPEAR-M0 model.

This driver requires every analysis choice at the command line. It does not
select records, scale factors or damping ratios on behalf of the researcher.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent / "jeong_elnashai"
sys.path.insert(0, str(MODEL_DIR))

import openseespy.opensees as ops  # noqa: E402
import spear_m0_jeong_elnashai_nonlinear as m0  # noqa: E402
from ground_motion import read_ground_motion  # noqa: E402


def rayleigh_coefficients(zeta: float, periods_s: tuple[float, float]) -> tuple[float, float]:
    if not (0.0 <= zeta < 1.0):
        raise ValueError("damping ratio must satisfy 0 <= zeta < 1")
    w1, w2 = (2.0 * math.pi / period for period in periods_s)
    beta_k = 2.0 * zeta / (w1 + w2)
    alpha_m = beta_k * w1 * w2
    return alpha_m, beta_k


def run(args) -> int:
    motion = read_ground_motion(args.record, args.record_dt, args.record_unit, args.scale)
    names, nt, masters = m0.build()
    periods_pre, _ = m0.first_mode_for_direction(masters, args.direction)
    if m0.gravity(names, nt) != 0:
        raise RuntimeError("gravity analysis failed")
    alpha_m, beta_k = rayleigh_coefficients(
        args.damping_ratio, (periods_pre[args.damping_mode_1 - 1], periods_pre[args.damping_mode_2 - 1])
    )
    ops.rayleigh(alpha_m, 0.0, 0.0, beta_k)
    ops.wipeAnalysis()
    ops.timeSeries("Path", 100, "-dt", motion.dt_s, "-values", *motion.values_m_s2)
    ops.pattern("UniformExcitation", 100, args.direction, "-accel", 100)
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", args.tolerance, args.max_iterations)
    ops.algorithm("Newton")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.analysis("Transient")

    out = args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    roof = masters[-1]
    initial_roof_disp = ops.nodeDisp(roof, args.direction)
    rows = [(0.0, 0.0, 0.0)]
    ok = 0
    for _ in range(len(motion.values_m_s2) - 1):
        ok = ops.analyze(1, motion.dt_s)
        if ok != 0:
            break
        rows.append((
            ops.getTime(),
            ops.nodeDisp(roof, args.direction) - initial_roof_disp,
            ops.nodeAccel(roof, args.direction),
        ))
    with out.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("time_s", "roof_displacement_m", "roof_relative_acceleration_m_s2"))
        writer.writerows(rows)
    summary = {
        "status": "COMPLETE" if ok == 0 and len(rows) == len(motion.values_m_s2) else "INCOMPLETE",
        "model": "SPEAR-M0-engineering-accepted-2026-10-29",
        "record": motion.source,
        "record_dt_s": motion.dt_s,
        "record_unit": motion.original_unit,
        "scale_factor": motion.scale_factor,
        "pga_m_s2": motion.pga_m_s2,
        "direction_dof": args.direction,
        "damping_ratio": args.damping_ratio,
        "damping_modes": [args.damping_mode_1, args.damping_mode_2],
        "rayleigh_alpha_m": alpha_m,
        "rayleigh_beta_k_current": beta_k,
        "completed_steps": len(rows) - 1,
        "requested_steps": len(motion.values_m_s2) - 1,
        "analysis_exit_code": ok,
        "initial_gravity_roof_displacement_m_removed": initial_roof_disp,
        "peak_abs_roof_displacement_m": max(abs(row[1]) for row in rows),
    }
    out.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    ops.wipe()
    return 0 if summary["status"] == "COMPLETE" else 3


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("record", type=Path)
    p.add_argument("--record-dt", type=float, required=True)
    p.add_argument("--record-unit", choices=("g", "m/s2", "cm/s2"), required=True)
    p.add_argument("--scale", type=float, required=True)
    p.add_argument("--direction", type=int, choices=(1, 2), required=True)
    p.add_argument("--damping-ratio", type=float, required=True)
    p.add_argument("--damping-mode-1", type=int, default=1)
    p.add_argument("--damping-mode-2", type=int, default=3)
    p.add_argument("--tolerance", type=float, default=1e-7)
    p.add_argument("--max-iterations", type=int, default=100)
    p.add_argument("--output", type=Path, required=True)
    return p


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))

