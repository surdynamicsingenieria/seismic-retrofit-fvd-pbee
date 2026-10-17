"""SPEAR Jeong-Elnashai nonlinear M0 — independent pushover diagnostic.

Derived only from MAE 04-03 source-locked reconstruction.
No Stratan-Fajfar hinges and no modal/capacity calibration.

Gate status:
- modal geometry/mass properties inherited from spear_m0_jeong_elnashai.py;
- distributed-plasticity fibre columns, P-Delta, rigid joint offsets/C6 arms;
- source-locked fibre T beams with the Fig. 2.3 typical bent-bar layout;
- pushover patterns follow MAE 04-03 Eq. 2.5 and Fig. 2.7.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import openseespy.opensees as ops

from geometry_source import BEAMS, BEFF_MM, JOINTS as PLAN, SLAB_THICKNESS, STORY_CENTERLINES
from pushover_patterns import get_pattern
from reinforcement_source import BAR_DIAMETER_M, COVER_M

OUT = Path("results/SPEAR/jeong_elnashai/pushover")
OUT.mkdir(parents=True, exist_ok=True)
Z = list(STORY_CENTERLINES)
GACC = 9.807
# DIAGNOSTIC ONLY: floor tuples originate in the Stratan-Fajfar SPEAR model,
# not in a recovered Jeong-Elnashai ZeusNL nodal mass input deck.
MASSES = [65.5e3, 65.5e3, 64.1e3]
POLAR = [1254e3, 1254e3, 1196e3]
CM = [(4.53, 5.29), (4.53, 5.29), (4.57, 5.33)]
PENDING_SOURCE_DATA = [
    "dimensioned longitudinal transition location of the Fig 2.3 bent bars",
    "Jeong-Elnashai Fig 2.6 nodal gravity and mass ledger; current floor tuples are Stratan-Fajfar inputs",
]


def fiber_rect(sec, conc, steel, b, h, nbar=4, bar_d=0.012):
    ops.section("Fiber", sec, "-GJ", 1e8)
    ops.patch("rect", conc, 14, 14, -b / 2, -h / 2, b / 2, h / 2)
    cover = COVER_M
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


def fiber_t_beam(sec, conc, steel, beff, top_bars, bottom_bars, gj):
    """Fig. 2.3 T beam, with the published typical longitudinal bars.

    The section datum is the 500 mm total-depth beam centreline.  The 150 mm
    slab forms the upper flange.  Published 15 mm cover is treated as clear
    cover to the outside of the Phi8 stirrup; longitudinal-bar centroids are
    consequently cover + stirrup diameter + half a Phi12 from the surface.
    """
    web = 0.25
    depth = 0.50
    slab = SLAB_THICKNESS
    stirrup_d = BAR_DIAMETER_M["phi8"]
    bar_d = BAR_DIAMETER_M["phi12"]
    bar_area = math.pi * bar_d**2 / 4.0
    centroid_cover = COVER_M + stirrup_d + bar_d / 2.0

    ops.section("Fiber", sec, "-GJ", gj)
    # Local section z is vertical for the horizontal-member transformations.
    ops.patch("rect", conc, 10, 6, -web / 2, -depth / 2, web / 2, depth / 2 - slab)
    ops.patch("rect", conc, 16, 4, -beff / 2, depth / 2 - slab, beff / 2, depth / 2)

    def bar_row(number, z):
        if number == 1:
            ys = (0.0,)
        else:
            edge = web / 2 - centroid_cover
            ys = tuple(-edge + 2 * edge * i / (number - 1) for i in range(number))
        for y in ys:
            ops.fiber(y, z, bar_area, steel)

    bar_row(top_bars, depth / 2 - centroid_cover)
    bar_row(bottom_bars, -depth / 2 + centroid_cover)


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

    # Five-point Gauss-Lobatto integration, matching the published University
    # of Rome OpenSees formulation.  Fig. 2.3 shows two of the four bottom
    # bars bent to the top at both ends: use 4-top/2-bottom at the two end
    # integration points and the A-A' 2-top/4-bottom section internally.
    lobatto_x = (0.0, 0.1726731646460114, 0.5, 0.8273268353539886, 1.0)
    lobatto_w = (0.05, 49.0 / 180.0, 16.0 / 45.0, 49.0 / 180.0, 0.05)
    beam_integrations = {}
    for j, (bn, _a, _b) in enumerate(BEAMS):
        beff = BEFF_MM[bn] / 1000.0
        # Saint-Venant thin-rectangle sum for the web and flange; this is a
        # geometric property, not a fitted stiffness parameter.
        jtors = (0.35 * 0.25**3 + beff * SLAB_THICKNESS**3) / 3.0
        sec_end = 3000 + 2 * j
        sec_mid = sec_end + 1
        fiber_t_beam(sec_end, 1, 2, beff, top_bars=4, bottom_bars=2, gj=gmod * jtors)
        fiber_t_beam(sec_mid, 1, 2, beff, top_bars=2, bottom_bars=4, gj=gmod * jtors)
        integ = 300 + j
        ops.beamIntegration(
            "UserDefined", integ, 5,
            sec_end, sec_mid, sec_mid, sec_mid, sec_end,
            *lobatto_x, *lobatto_w,
        )
        beam_integrations[bn] = integ

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
            ops.element(
                "forceBeamColumn", 10000 + k * 100 + j, ni, nj, tr,
                beam_integrations[bn], "-iter", 50, 1e-10,
            )

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


def apply_pushover_loads(case_name, masters, nt, periods, phi):
    dof = 1 if case_name[0] == "x" else 2
    rows = get_pattern(case_name, phi, MASSES)
    ops.timeSeries("Linear", 20)
    ops.pattern("Plain", 20, 20)
    # Fig. 2.7 does not apply the floor resultant at the centre of mass.  Its
    # three frame forces deliberately create the published floor torque.  With
    # a rigid diaphragm the forces may be placed at the shown perimeter joints
    # and the Transformation constraint handler transfers both resultant and
    # moment to the master node.
    loading_points = {
        "xp100": ("C8", "C9", "C5"),   # bottom, middle, top; left edge
        "xn100": ("C7", "C4", "C2"),   # bottom, middle, top; right edge
        "yp100": ("C8", "C6", "C7"),   # left, middle, right; bottom edge
        "yn100": ("C5", "C1", "C2"),   # left, middle, right; top edge
    }[case_name]
    for k, frame_row in enumerate(rows, start=1):
        for joint, q in zip(loading_points, frame_row):
            ops.load(nt(k, joint), q if dof == 1 else 0, q if dof == 2 else 0, 0, 0, 0, 0)
    return periods, phi, rows


def run(case_name="xp100", target_mm=200.0, du_mm=0.5):
    names, nt, masters = build()
    dof = 1 if case_name[0] == "x" else 2
    periods_pre_gravity, phi_pre_gravity = first_mode_for_direction(masters, dof)
    if gravity(names, nt) != 0:
        raise RuntimeError("gravity analysis failed")

    sign = -1 if case_name[1] == "n" else 1
    periods_post_gravity, _phi_post_gravity = first_mode_for_direction(masters, dof)
    phi = phi_pre_gravity
    periods_for_pattern = periods_pre_gravity
    _periods, _phi, pattern_rows = apply_pushover_loads(
        case_name, masters, nt, periods_for_pattern, phi
    )

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
        "periods_s": periods_post_gravity,
        "periods_pre_gravity_s": periods_pre_gravity,
        "periods_post_gravity_s": periods_post_gravity,
        "modal_state_used_for_eq_2_5": "pre-gravity eigenvalue state",
        "first_mode_shape_used_for_eq_2_5": phi,
        "fig_2_7_pattern_rows": pattern_rows,
        "fig_2_7_load_application": "three perimeter frame points per floor, not floor CM",
        "reached_top_displacement_mm": output[-1][0],
        "completed_steps": len(output) - 1,
        "requested_steps": requested_steps,
        "fallback_attempts": retries,
        "analysis_exit_code": ok,
        "peak_abs_base_shear_kN": max(abs(v) for _, v in output),
        "pending_source_data": PENDING_SOURCE_DATA,
        "acceptance": "PROHIBITED until Fig 2.6 gravity/mass allocation is source-locked and modal/capacity errors close",
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
