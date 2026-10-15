"""Jeong-Elnashai MAE 04-03 SPEAR M0 diagnostic modal model.

No Stratan-Fajfar hinge data. No modal calibration.
"""
import json
import math
from pathlib import Path

import openseespy.opensees as ops

from geometry_source import BEAMS, BEFF_MM, JOINTS as PLAN, SLAB_THICKNESS, STORY_CENTERLINES

OUT = Path("results/SPEAR/jeong_elnashai")
OUT.mkdir(parents=True, exist_ok=True)
Z = list(STORY_CENTERLINES)
GAMMA_RC = 24.518


def rect(sec, mat, b, h):
    ops.section("Fiber", sec, "-GJ", 1.0e8)
    ops.patch("rect", mat, 12, 12, -b / 2, -h / 2, b / 2, h / 2)


def polygon_area(poly):
    return 0.5 * abs(sum(
        poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
        for i in range(len(poly))
    ))


def build():
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    fc = 25.0e6
    Es = 206.0e9
    fy12 = 458.67e6
    Ec = 4700.0 * math.sqrt(25.0) * 1.0e6
    ops.uniaxialMaterial("Concrete02", 1, -fc, -0.002, -0.2 * fc, -0.006, 0.1, 0.0, 0.0)
    ops.uniaxialMaterial("Steel02", 2, fy12, Es, 0.0032, 18.0, 0.925, 0.15)
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

    rect(101, 1, 0.25, 0.25)
    rect(102, 1, 0.75, 0.25)
    ops.beamIntegration("Lobatto", 201, 101, 5)
    ops.beamIntegration("Lobatto", 202, 102, 5)

    Er = Ec * 1.0e4
    Gr = Er / (2 * 1.2)
    for k in range(1, 4):
        trr = 6000 + k
        ops.geomTransf("Linear", trr, 0, 0, 1)
        ops.element("elasticBeamColumn", 60000 + k * 10 + 5, nt(k, "C6"), 8000 + k * 10 + 5, 1.0, Er, Gr, 1.0, 1.0, 1.0, trr)
        ops.element("elasticBeamColumn", 60000 + k * 10 + 6, nt(k, "C6"), 8000 + k * 10 + 6, 1.0, Er, Gr, 1.0, 1.0, 1.0, trr)

    et = 1
    for k in range(1, 4):
        for n in names:
            trc = 5000 + k * 100 + ix[n]
            bot = 0.0 if k == 1 else 0.25
            ops.geomTransf("PDelta", trc, 1, 0, 0, "-jntOffset", 0, 0, bot, 0, 0, -0.25)
            ops.element("dispBeamColumn", et, nt(k - 1, n), nt(k, n), trc, 202 if n == "C6" else 201)
            et += 1

    for k in range(1, 4):
        for j, (bn, a, b) in enumerate(BEAMS):
            beff = BEFF_MM[bn] / 1000.0
            area = 0.25 * 0.50 + (beff - 0.25) * SLAB_THICKNESS
            af = beff * SLAB_THICKNESS
            aw = 0.25 * (0.50 - SLAB_THICKNESS)
            zf = 0.50 - SLAB_THICKNESS / 2
            zw = (0.50 - SLAB_THICKNESS) / 2
            zbar = (af * zf + aw * zw) / (af + aw)
            iy = beff * SLAB_THICKNESS**3 / 12 + af * (zf - zbar)**2 + 0.25 * (0.50 - SLAB_THICKNESS)**3 / 12 + aw * (zw - zbar)**2
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
            off_j = 0.375 if (bn == "B10" and b == "C6") else 0.125
            tr = 7000 + k * 100 + j
            ops.geomTransf("Linear", tr, 0, 0, 1, "-jntOffset", 0.125 * ux, 0.125 * uy, 0.0, -off_j * ux, -off_j * uy, 0.0)
            ops.element("elasticBeamColumn", 10000 + k * 100 + j, ni, nj, area, Ec, Ec / (2 * 1.2), jtors, iy, iz, tr)

    # DIAGNOSTIC ONLY: these tuples are documented in the Stratan-Fajfar
    # SPEAR model, not as the Jeong-Elnashai nodal mass ledger in MAE 04-03.
    # They must not be accepted as source-equivalent UIUC/ZeusNL inputs.
    floor_mass_t = {1: 65.5, 2: 65.5, 3: 64.1}
    floor_cm = {1: (4.53, 5.29), 2: (4.53, 5.29), 3: (4.57, 5.33)}
    floor_jm_tm2 = {1: 1254.0, 2: 1254.0, 3: 1196.0}
    masters = []
    for k in range(1, 4):
        master = 900 + k
        ops.node(master, *floor_cm[k], Z[k])
        ops.fix(master, 0, 0, 1, 1, 1, 0)
        ops.mass(master, 1000.0 * floor_mass_t[k], 1000.0 * floor_mass_t[k], 0, 0, 0, 1000.0 * floor_jm_tm2[k])
        ops.rigidDiaphragm(3, master, *([nt(k, n) for n in names] + [8000 + k * 10 + 5, 8000 + k * 10 + 6]))
        masters.append(master)
    return names, nt, masters


def modal():
    build()
    vals = ops.eigen("-fullGenLapack", 4)
    periods = [2 * math.pi / math.sqrt(v) for v in vals]
    target = [0.51, 0.46, 0.40, 0.18]
    err = [100 * (a - b) / b for a, b in zip(periods, target)]
    out = {"periods_s": periods, "targets_s": target, "errors_pct": err}
    (OUT / "modal_baseline.json").write_text(json.dumps(out, indent=2))
    print("JEONG_ELNASHAI_MODAL", json.dumps(out))
    ops.wipe()
    return out


if __name__ == "__main__":
    modal()
