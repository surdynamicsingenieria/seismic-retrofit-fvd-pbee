"""Audit elastic-vs-fibre initial T-beam stiffness without OpenSees fitting."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "SPEAR" / "jeong_elnashai"
sys.path.insert(0, str(MODEL))

from geometry_source import BEFF_MM, SLAB_THICKNESS  # noqa: E402
from reinforcement_source import BAR_DIAMETER_M, COVER_M  # noqa: E402

EC_ELASTIC = 4700.0 * math.sqrt(25.0) * 1.0e6
# OpenSees Concrete02 initial tangent = 2*fpc/epsc0 for the production inputs.
EC_FIBRE = 2.0 * 25.0e6 / 0.002
ES = 206.0e9
WEB = 0.25
DEPTH = 0.50
BAR_D = BAR_DIAMETER_M["phi12"]
BAR_AREA = math.pi * BAR_D**2 / 4.0
BAR_OFFSET = COVER_M + BAR_DIAMETER_M["phi8"] + BAR_D / 2.0


def concrete_parts(beff: float) -> list[tuple[float, float, float]]:
    """Return area, centroid-from-bottom and centroidal I for web/flange."""
    web_h = DEPTH - SLAB_THICKNESS
    return [
        (WEB * web_h, web_h / 2.0, WEB * web_h**3 / 12.0),
        (beff * SLAB_THICKNESS, DEPTH - SLAB_THICKNESS / 2.0,
         beff * SLAB_THICKNESS**3 / 12.0),
    ]


def section_ei(beff: float, top_bars: int, bottom_bars: int) -> tuple[float, float]:
    parts = [(EC_FIBRE * a, z, EC_FIBRE * ic) for a, z, ic in concrete_parts(beff)]
    for number, z in ((bottom_bars, BAR_OFFSET), (top_bars, DEPTH - BAR_OFFSET)):
        parts.extend((ES * BAR_AREA, z, 0.0) for _ in range(number))
    ea = sum(ea_i for ea_i, _z, _ei in parts)
    zbar = sum(ea_i * z for ea_i, z, _ei in parts) / ea
    ei = sum(ei_i + ea_i * (z - zbar) ** 2 for ea_i, z, ei_i in parts)
    return ea, ei


def elastic_ei(beff: float) -> float:
    parts = concrete_parts(beff)
    area = sum(a for a, _z, _i in parts)
    zbar = sum(a * z for a, z, _i in parts) / area
    inertia = sum(ic + a * (z - zbar) ** 2 for a, z, ic in parts)
    return EC_ELASTIC * inertia


def main() -> int:
    rows = []
    for beam, beff_mm in BEFF_MM.items():
        beff = beff_mm / 1000.0
        base = elastic_ei(beff)
        _ea_end, ei_end = section_ei(beff, top_bars=4, bottom_bars=2)
        _ea_mid, ei_mid = section_ei(beff, top_bars=2, bottom_bars=4)
        rows.append({
            "beam": beam,
            "beff_mm": beff_mm,
            "elastic_EI_Nm2": base,
            "fibre_end_EI_Nm2": ei_end,
            "fibre_mid_EI_Nm2": ei_mid,
            "end_vs_elastic_pct": 100.0 * (ei_end / base - 1.0),
            "mid_vs_elastic_pct": 100.0 * (ei_mid / base - 1.0),
        })
    result = {
        "status": "AUDIT_ONLY",
        "elastic_concrete_modulus_Pa": EC_ELASTIC,
        "Concrete02_initial_tangent_Pa": EC_FIBRE,
        "material_tangent_difference_pct": 100.0 * (EC_FIBRE / EC_ELASTIC - 1.0),
        "steel_fibres_overlay_concrete": True,
        "sections": rows,
    }
    out = ROOT / "results" / "SPEAR" / "jeong_elnashai" / "beam_section_initial_stiffness_audit.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
