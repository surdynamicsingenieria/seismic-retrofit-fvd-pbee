"""Simultaneous two-horizontal-component NLTHA for the locked SPEAR-M0 model."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent / "jeong_elnashai"
sys.path.insert(0, str(MODEL_DIR))

import openseespy.opensees as ops  # noqa: E402
import spear_m0_jeong_elnashai_nonlinear as m0  # noqa: E402
from ground_motion import GroundMotion, read_ground_motion, read_peer_at2  # noqa: E402
from record_manifest import validated_horizontal_pairs  # noqa: E402
from run_baseline_nltha import analyze_interval, rayleigh_coefficients  # noqa: E402


def _motion(manifest: Path, record: dict) -> GroundMotion:
    source = (manifest.parent / record["path"]).resolve()
    if source.suffix.upper() == ".AT2":
        motion = read_peer_at2(source, record["unit"], record["scale_factor"])
        if abs(motion.dt_s - record["dt_s"]) > 1e-12:
            raise ValueError(f"manifest/header DT mismatch for {record['record_id']}")
        return motion
    return read_ground_motion(source, record["dt_s"], record["unit"], record["scale_factor"])


def _padded(values: tuple[float, ...], length: int) -> tuple[float, ...]:
    return values + (0.0,) * (length - len(values))


def run(args) -> int:
    available = validated_horizontal_pairs(args.manifest)
    selected = [(x, y) for x, y in available if x["pair_id"] == args.pair_id]
    if len(selected) != 1:
        raise ValueError(f"pair_id {args.pair_id!r} not found exactly once")
    x_record, y_record = selected[0]
    x_motion, y_motion = _motion(args.manifest, x_record), _motion(args.manifest, y_record)
    sample_count = max(len(x_motion.values_m_s2), len(y_motion.values_m_s2))
    x_values = _padded(x_motion.values_m_s2, sample_count)
    y_values = _padded(y_motion.values_m_s2, sample_count)

    names, nt, masters = m0.build()
    periods, _ = m0.first_mode_for_direction(masters, 1)
    if m0.gravity(names, nt) != 0:
        raise RuntimeError("gravity analysis failed")
    alpha_m, beta_k = rayleigh_coefficients(
        args.damping_ratio, (periods[args.damping_mode_1 - 1], periods[args.damping_mode_2 - 1])
    )
    ops.rayleigh(alpha_m, 0.0, 0.0, beta_k)
    ops.wipeAnalysis()
    for tag, dof, values in ((101, 1, x_values), (102, 2, y_values)):
        ops.timeSeries("Path", tag, "-dt", x_motion.dt_s, "-values", *values)
        ops.pattern("UniformExcitation", tag, dof, "-accel", tag)
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", args.tolerance, args.max_iterations)
    ops.algorithm("Newton")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.analysis("Transient")

    roof = masters[-1]
    centre_nodes = [nt(k, "C3") for k in range(1, 4)]
    base_nodes = [nt(0, name) for name in names]
    initial_roof = {dof: ops.nodeDisp(roof, dof) for dof in (1, 2)}
    initial_centre = {dof: [ops.nodeDisp(n, dof) for n in centre_nodes] for dof in (1, 2)}
    rows = [(0.0,) + (0.0,) * 16]
    ok = 0
    fallback_counts = {"KrylovNewton": 0, "NewtonLineSearch": 0, "two-half-steps": 0}
    for step in range(1, sample_count):
        ok, algorithm = analyze_interval(x_motion.dt_s, args.tolerance, args.max_iterations)
        if ok != 0:
            break
        if algorithm in fallback_counts:
            fallback_counts[algorithm] += 1
        axis_values = []
        for dof, ground_accel in ((1, x_values[step]), (2, y_values[step])):
            disp = [ops.nodeDisp(n, dof) - initial for n, initial in zip(centre_nodes, initial_centre[dof])]
            drift = (disp[0] / 3.0, (disp[1] - disp[0]) / 3.0, (disp[2] - disp[1]) / 3.0)
            floor_accel = tuple(ops.nodeAccel(master, dof) + ground_accel for master in masters)
            ops.reactions()
            base_shear = -sum(ops.nodeReaction(node, dof) for node in base_nodes) / 1000.0
            axis_values.extend((ops.nodeDisp(roof, dof) - initial_roof[dof], *drift, *floor_accel, base_shear))
        rows.append((ops.getTime(), *axis_values))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    axis_headers = []
    for axis in ("x", "y"):
        axis_headers.extend((f"roof_displacement_{axis}_m", *(f"story_{i}_drift_ratio_{axis}" for i in range(1, 4)),
                             *(f"floor_{i}_absolute_acceleration_{axis}_m_s2" for i in range(1, 4)),
                             f"base_shear_{axis}_kN"))
    with args.output.open("w", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("time_s", *axis_headers))
        writer.writerows(rows)

    def peaks(indices):
        return [max(abs(row[i]) for row in rows) for i in indices]

    summary = {
        "status": "COMPLETE" if ok == 0 and len(rows) == sample_count else "INCOMPLETE",
        "model": "SPEAR-M0-engineering-accepted-2026-10-29",
        "pair_id": args.pair_id,
        "record_ids": {"X": x_record["record_id"], "Y": y_record["record_id"]},
        "record_dt_s": x_motion.dt_s,
        "component_sample_counts": {"X": len(x_motion.values_m_s2), "Y": len(y_motion.values_m_s2)},
        "zero_padding_samples": {"X": sample_count - len(x_motion.values_m_s2), "Y": sample_count - len(y_motion.values_m_s2)},
        "pga_m_s2": {"X": x_motion.pga_m_s2, "Y": y_motion.pga_m_s2},
        "damping_ratio": args.damping_ratio,
        "damping_modes": [args.damping_mode_1, args.damping_mode_2],
        "rayleigh_alpha_m": alpha_m,
        "rayleigh_beta_k_current": beta_k,
        "completed_steps": len(rows) - 1,
        "requested_steps": sample_count - 1,
        "analysis_exit_code": ok,
        "fallback_counts": fallback_counts,
        "peak_abs_roof_displacement_m": {"X": peaks((1,))[0], "Y": peaks((9,))[0]},
        "peak_abs_story_drift_ratio": {"X": peaks((2, 3, 4)), "Y": peaks((10, 11, 12))},
        "peak_abs_floor_acceleration_m_s2": {"X": peaks((5, 6, 7)), "Y": peaks((13, 14, 15))},
        "peak_abs_base_shear_kN": {"X": peaks((8,))[0], "Y": peaks((16,))[0]},
    }
    args.output.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    ops.wipe()
    return 0 if summary["status"] == "COMPLETE" else 3


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    p.add_argument("--pair-id", required=True)
    p.add_argument("--damping-ratio", type=float, required=True)
    p.add_argument("--damping-mode-1", type=int, default=1)
    p.add_argument("--damping-mode-2", type=int, default=3)
    p.add_argument("--tolerance", type=float, default=1e-7)
    p.add_argument("--max-iterations", type=int, default=100)
    p.add_argument("--output", type=Path, required=True)
    return p


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
