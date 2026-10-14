"""SPEAR Jeong-Elnashai nonlinear M0 — independent pushover diagnostic.

Derived only from MAE 04-03 source-locked reconstruction.
No Stratan-Fajfar hinges and no modal/capacity calibration.

Gate status:
- modal geometry/mass properties inherited from spear_m0_jeong_elnashai.py;
- distributed-plasticity fibre columns, P-Delta, rigid joint offsets/C6 arms;
- beams keep elastic source-derived T-section stiffness until the exact
  reinforcement schedule is locked;
- pushover patterns follow MAE 04-03 Eq. 2.5 and Fig. 2.7.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import openseespy.opensees as ops

from geometry_source import BEAMS, BEFF_MM, JOINTS as PLAN, SLAB_THICKNESS, STORY_CENTERLINES
from pushover_patterns import get_pattern

OUT = Path("results/SPEAR/jeong_elnashai/pushover")
OUT.mkdir(parents=True, exist_ok=True)
Z = list(STORY_CENTERLINES)
GACC = 9.807
MASSES = [65.5e3, 65.5e3, 64.1e3]
POLAR = [1254e3, 1254e3, 1196e3]
CM = [(4.53, 5.29), (4.53, 5.29), (4.57, 5.33)]
PENDING_SOURCE_DATA = [
    "complete beam reinforcement by member/storey",
    "complete column reinforcement by member/storey",
    "Fig 2.6 exact nodal gravity allocation",
]


def fiber_rect(sec, conc, steel, b, h, nbar=4, bar_d=0.012):
    ops.section("Fiber", sec, "-GJ", 1e8)
    ops.patch("rect", conc, 14, 14, -b / 2, -h / 2, b / 2, h / 2)
    cover = 0.031
    area_bar = math.pi * bar_d**2 / 4
    if nbar == 4:
        for y in (-b / 2 + cover, b / 2 - cover):
            for z in (-h / 2 + cover, h / 2 - cover):
                ops.fiber(y, z, area_bar, steel)
    else:
        for z in (-h / 2 + cover, h / 2 - cover):
            for i in range(nbar // 2):
                y = -b / 2 + cover + (b - 2 * cover) * i / (nbar // 2 - 1)
                ops.fiber(y, z, area_bar, steel)


def build():
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    fc = 25e6
    es = 206e9
    fy = 458.67e6
    ec = 4700 * math.sqrt(25) * 1e6
    gmod = ec / (2 * 1.2)
    ops.uniaxialMaterial("Concrete02", 1, -fc, -0.002, -0.2 * fc, -0.006, 0.1, 0, 0)
    ops.uniaxialMaterial("Steel02", 2, fy, es, 0.0032, 18, 0.925, 0.15)
    names = list(PLAN)
    ix = {n: i + 1 for i, n in enumerate(names)}

    def nt(k, n):
        return 100 * k + ix[n]

    for k, z in enumerate(Z):
        for n, (x, y) in PLAN.items():
            ops.node(nt(k, n), x, y, z)
            if k == 0:
                ops.fix(nt(k, n), 1, 1, 1, 1, 1, 1)
        ops.node(8000 + k * 10 + 5, PLAN["C6"][0], PLAN["C6"][1] - 0.25, z)
        ops.node(8000 + k * 10 + 6, PLAN["C6"][0], PLAN["C6"][1] + 0.25, z)
        if k == 0:
            ops.fix(8000 + k * 10 + 5, 1, 1, 1, 1, 1, 1)
            ops.fix(8000 + k * 10 + 6, 1, 1, 1, 1, 1, 1)

    fiber_rect(101, 1, 2, 0.25, 0.25, 4)
    fiber_rect(102, 1, 2, 0.75, 0.25, 10)
    ops.beamIntegration("Lobatto", 201, 101, 5)
    ops.beamIntegration("Lobatto", 202, 102, 5)

    er = ec * 1e4
    gr = er / (2 * 1.2)
    for k in range(1, 4):
        tr = 6000 + k
        ops.geomTransf("Linear", tr, 0, 0, 1)
        for q in (5, 6):
            ops.element("elasticBeamColumn", 60000 + k * 10 + q, nt(k, "C6"), 8000 + k * 10 + q, 1.0, er, gr, 1.0, 1.0, 1.0, tr)

    et = 1
    for k in range(1, 4):
        for n in names:
            tr = 5000 + k * 100 + ix[n]
            bot = 0 if k == 1 else 0.25
            ops.geomTransf("PDelta", tr, 1, 0, 0, "-jntOffset", 0, 0, bot, 0, 0, -0.25)
            ops.element("dispBeamColumn", et, nt(k - 1, n), nt(k, n), tr, 202 if n == "C6" else 201)
            et += 1

    for k in range(1, 4):
        for j, (bn, a, b) in enumerate(BEAMS):
            beff = BEFF_MM[bn] / 1000.0
            area = 0.25 * 0.50 + (beff - 0.25) * SLAB_THICKNESS
            af = beff * SLAB_THICKNESS
            aw = 0.25 * (0.50 - SLAB_THICKNESS)
            zf = 0.50 - SLAB_THICKNESS / 2
            zw = (0.50 - SLAB_THICKNESS) / 2
            zb = (af * zf + aw * zw) / (af + aw)
            iy = beff * SLAB_THICKNESS**3 / 12 + af * (zf - zb) ** 2 + 0.25 * (0.50 - SLAB_THICKNESS) ** 3 / 12 + aw * (zw - zb) ** 2
            iz = 0.50 * 0.25**3 / 12
            jtors = 0.25 * 0.50**3 / 3
            xa, ya = PLAN[a]
            xb, yb = PLAN[b]
            ni, nj = nt(k, a), nt(k, b)
            if bn == "B5" and b == "C6":
                xb, yb = PLAN["C6"][0], PLAN["C6"][1] - 0.25
                nj = 8000 + k * 10 + 5
            if bn == "B6" and a == "C6":
                xa, ya = PLAN["C6"][0], PLAN["C6"][1] + 0.25
                ni = 8000 + k * 10 + 6
            length = math.hypot(xb - xa, yb - ya)
            ux, uy = (xb - xa) / length, (yb - ya) / length
            off_i = 0.125
            off_j = 0.375 if bn == "B10" and b == "C6" else 0.125
            tr = 7000 + k * 100 + j
            ops.geomTransf("Linear", tr, 0, 0, 1, "-jntOffset", off_i * ux, off_i * uy, 0, -off_j * ux, -off_j * uy, 0)
            ops.element("elasticBeamColumn", 10000 + k * 100 + j, ni, nj, area, ec, gmod, jtors, iy, iz, tr)

    masters = []
    for k in range(1, 4):
        master = 900 + k
        cx, cy = CM[k - 1]
        ops.node(master, cx, cy, Z[k])
        ops.fix(master, 0, 0, 1, 1, 1, 0)
        ops.mass(master, MASSES[k - 1], MASSES[k - 1], 0, 0, 0, POLAR[k - 1])
        ops.rigidDiaphragm(3, master, *([nt(k, n) for n in names] + [8000 + k * 10 + 5, 8000 + k * 10 + 6]))
        masters.append(master)
    return names, nt, masters


def gravity(names, nt):
    ops.timeSeries("Linear", 10)
    ops.pattern("Plain", 10, 10)
    for k in range(1, 4):
        weight = MASSES[k - 1] * GACC / len(names)
        for n in names:
            ops.load(nt(k, n), 0, 0, -weight, 0, 0, 0)
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", 1e-8, 50)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.1)
    ops.analysis("Static")
    ok = ops.analyze(10)
    if ok == 0:
        ops.loadConst("-time", 0)
    return ok


def first_mode_for_direction(masters, dof):
    values = ops.eigen("-fullGenLapack", 4)
    periods = [2 * math.pi / math.sqrt(value) for value in values]
    phi = [ops.nodeEigenvector(master, 1, dof) for master in masters]
    if sum(mass * value for mass, value in zip(MASSES, phi)) < 0:
        phi = [-value for value in phi]
    return periods, phi


def apply_pushover_loads(case_name, masters):
    dof = 1 if case_name[0] == "x" else 2
    periods, phi = first_mode_for_direction(masters, dof)
    rows = get_pattern(case_name, phi, MASSES)
    ops.timeSeries("Linear", 20)
    ops.pattern("Plain", 20, 20)
    # Current diagnostic model has one rigid-diaphragm master per floor. Apply
    # the floor-summed Eq. 2.5 force there, while storing Fig. 2.7 frame rows.
    for master, frame_row in zip(masters, rows):
        q = sum(frame_row)
        ops.load(master, q if dof == 1 else 0, q if dof == 2 else 0, 0, 0, 0, 0)
    return periods, phi, rows


def run(case_name="xp100", target_mm=200.0, du_mm=0.5):
    names, nt, masters = build()
    if gravity(names, nt) != 0:
        raise RuntimeError("gravity analysis failed")

    dof = 1 if case_name[0] == "x" else 2
    sign = -1 if case_name[1] == "n" else 1
    periods, phi, pattern_rows = apply_pushover_loads(case_name, masters)

    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", 1e-7, 80)
    ops.algorithm("Newton")
    ops.integrator("DisplacementControl", masters[-1], dof, sign * abs(du_mm) / 1000.0)
    ops.analysis("Static")

    output = [(0.0, 0.0)]
    base_nodes = [nt(0, n) for n in names]
    ok = 0
    retries = 0
    requested_steps = int(abs(target_mm / du_mm))
    for _ in range(requested_steps):
        ok = ops.analyze(1)
        if ok != 0:
            retries += 1
            ops.test("NormDispIncr", 1e-6, 160)
            ops.algorithm("NewtonLineSearch", 0.8)
            ops.integrator("DisplacementControl", masters[-1], dof, sign * abs(du_mm) / 4000.0)
            ok = ops.analyze(4)
            ops.algorithm("Newton")
            ops.test("NormDispIncr", 1e-7, 80)
            ops.integrator("DisplacementControl", masters[-1], dof, sign * abs(du_mm) / 1000.0)
        if ok != 0:
            break
        ops.reactions()
        disp_mm = 1000.0 * ops.nodeDisp(masters[-1], dof)
        base_shear_kn = -sum(ops.nodeReaction(n, dof) for n in base_nodes) / 1000.0
        output.append((disp_mm, base_shear_kn))

    out_csv = OUT / f"{case_name}.csv"
    out_csv.write_text(
        "top_displacement_mm,base_shear_kN\n"
        + "\n".join(f"{u:.6f},{v:.6f}" for u, v in output)
        + "\n"
    )
    summary = {
        "status": "DIAGNOSTIC_ONLY",
        "case": case_name,
        "periods_s": periods,
        "first_mode_shape_used_for_eq_2_5": phi,
        "fig_2_7_pattern_rows": pattern_rows,
        "reached_top_displacement_mm": output[-1][0],
        "completed_steps": len(output) - 1,
        "requested_steps": requested_steps,
        "fallback_attempts": retries,
        "analysis_exit_code": ok,
        "peak_abs_base_shear_kN": max(abs(v) for _, v in output),
        "pending_source_data": PENDING_SOURCE_DATA,
        "acceptance": "PROHIBITED until reinforcement and Fig 2.6 allocation are source-locked",
    }
    (OUT / f"{case_name}_summary.json").write_text(json.dumps(summary, indent=2))
    print("JEONG_ELNASHAI_PUSHOVER", json.dumps(summary))
    ops.wipe()
    return 0 if ok == 0 else 3


def run_all():
    exit_codes = {}
    for case_name in ("xp100", "xn100", "yp100", "yn100"):
        exit_codes[case_name] = run(case_name)
    return 0 if all(code == 0 for code in exit_codes.values()) else 3


if __name__ == "__main__":
    raise SystemExit(run_all())
