"""Source-bounded Fig. 2.6 beam-gravity sensitivity; not production input."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "SPEAR" / "jeong_elnashai"
sys.path.insert(0, str(MODEL_DIR))

import spear_m0_jeong_elnashai_nonlinear as model  # noqa: E402
from geometry_source import BEAMS, JOINTS, SLAB_PLAN_DIMS  # noqa: E402
from gravity_mass_source import NODE_WEIGHTS_KN  # noqa: E402

OUT = ROOT / "results" / "SPEAR" / "jeong_elnashai" / "sensitivity" / "fig_2_6_beam_gravity"
STATIONS = (0.0, 0.15, 0.50, 0.85, 1.0)


def beam_endpoints(name: str, a: str, b: str):
    pa, pb = JOINTS[a], JOINTS[b]
    if name == "B5":
        pb = (JOINTS["C6"][0], JOINTS["C6"][1] - 0.25)
    elif name == "B6":
        pa = (JOINTS["C6"][0], JOINTS["C6"][1] + 0.25)
    return pa, pb


def tributary_station_fractions(step=0.05):
    """Nearest-beam numerical integration of the published Fig. 2.6 rule."""
    accum = [[0.0] * 5 for _ in BEAMS]
    nx = round(SLAB_PLAN_DIMS[0] / step)
    ny = round(SLAB_PLAN_DIMS[1] / step)
    for ix in range(nx):
        x = (ix + 0.5) * SLAB_PLAN_DIMS[0] / nx
        for iy in range(ny):
            y = (iy + 0.5) * SLAB_PLAN_DIMS[1] / ny
            best = None
            for j, (name, a, b) in enumerate(BEAMS):
                p0, p1 = beam_endpoints(name, a, b)
                dx, dy = p1[0] - p0[0], p1[1] - p0[1]
                ll = dx * dx + dy * dy
                t = max(0.0, min(1.0, ((x - p0[0]) * dx + (y - p0[1]) * dy) / ll))
                qx, qy = p0[0] + t * dx, p0[1] + t * dy
                d2 = (x - qx) ** 2 + (y - qy) ** 2
                if best is None or d2 < best[0]:
                    best = (d2, j, t)
            _, j, t = best
            for m, (s0, s1) in enumerate(zip(STATIONS[:-1], STATIONS[1:])):
                if s0 <= t <= s1:
                    r = (t - s0) / (s1 - s0)
                    accum[j][m] += 1.0 - r
                    accum[j][m + 1] += r
                    break
    total = sum(sum(row) for row in accum)
    return [[value / total for value in row] for row in accum]


FRACTIONS = tributary_station_fractions()


def gravity_on_beams(names, nt):
    ops = model.ops
    ops.timeSeries("Linear", 10)
    ops.pattern("Plain", 10, 10)
    # Column self-weight is kept at joints; the remaining exact Table 3.1
    # floor weight is distributed to beam stations using Fig. 2.6 geometry.
    gamma = 24.518
    column_weights = {n: gamma * 3.0 * (0.75 * 0.25 if n == "C6" else 0.25 * 0.25) for n in names}
    audit = []
    for k in range(1, 4):
        floor_total = sum(NODE_WEIGHTS_KN[n][k - 1] for n in names)
        column_total = sum(column_weights.values())
        beam_total = floor_total - column_total
        for n in names:
            ops.load(nt(k, n), 0, 0, -1000.0 * column_weights[n], 0, 0, 0)
        applied = column_total
        for j, ((bn, a, b), row) in enumerate(zip(BEAMS, FRACTIONS)):
            endpoint_i = nt(k, a)
            endpoint_j = nt(k, b)
            if bn == "B5": endpoint_j = 8000 + k * 10 + 5
            if bn == "B6": endpoint_i = 8000 + k * 10 + 6
            tags = [endpoint_i, 300000 + k * 10000 + j * 10 + 1,
                    300000 + k * 10000 + j * 10 + 2,
                    300000 + k * 10000 + j * 10 + 3, endpoint_j]
            for tag, fraction in zip(tags, row):
                load = beam_total * fraction
                ops.load(tag, 0, 0, -1000.0 * load, 0, 0, 0)
                applied += load
        audit.append({"floor": k, "target_kN": floor_total, "applied_kN": applied})
    ops.constraints("Transformation"); ops.numberer("RCM"); ops.system("UmfPack")
    ops.test("NormDispIncr", 1e-8, 80); ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.1); ops.analysis("Static")
    ok = ops.analyze(10)
    if ok == 0: ops.loadConst("-time", 0)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gravity_balance.json").write_text(json.dumps(audit, indent=2) + "\n")
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="*", default=["xp100"])
    parser.add_argument("--target-mm", type=float, default=200.0)
    args = parser.parse_args()
    original_gravity, original_out = model.gravity, model.OUT
    model.gravity, model.OUT = gravity_on_beams, OUT / "pushover"
    model.OUT.mkdir(parents=True, exist_ok=True)
    try:
        return max(model.run(case, target_mm=args.target_mm) for case in args.cases)
    finally:
        model.gravity, model.OUT = original_gravity, original_out


if __name__ == "__main__":
    raise SystemExit(main())
