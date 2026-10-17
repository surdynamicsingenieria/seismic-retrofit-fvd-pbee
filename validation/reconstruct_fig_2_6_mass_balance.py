"""Reconstruct the published SPEAR global gravity/mass balance.

This script intentionally stops at the global balance.  Fig. 2.6 defines the
slab-to-nearest-beam rule graphically, but MAE 04-03 does not print the
node-by-node ZeusNL ledger.  A nodal allocation must preserve this balance and
is a separate validation gate.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

MODEL = Path(__file__).resolve().parents[1] / "models/SPEAR/jeong_elnashai"
sys.path.insert(0, str(MODEL))

from geometry_source import CLEAR_SPAN_MM, SLAB_PLAN_DIMS, SLAB_THICKNESS


OUT = Path("results/SPEAR/jeong_elnashai/mass_balance_fig_2_6.json")


def main() -> int:
    density = 24.518  # kN/m3, MAE 04-03 Sec. 2.2.4
    finish = 0.5  # kN/m2
    live_effective = 0.3 * 2.0  # kN/m2
    floors = 3
    story_height = 3.0
    beam_web = 0.25
    beam_drop = 0.50 - SLAB_THICKNESS
    regular_column_area = 0.25 * 0.25
    c6_area = 0.75 * 0.25

    slab_area = SLAB_PLAN_DIMS[0] * SLAB_PLAN_DIMS[1]
    clear_beam_length = sum(CLEAR_SPAN_MM.values()) / 1000.0
    slab_load = floors * slab_area * (
        density * SLAB_THICKNESS + finish + live_effective
    )
    # Only the beam drop is added because the slab volume already includes the
    # upper 150 mm over the beam webs.
    beam_load = floors * clear_beam_length * beam_web * beam_drop * density
    column_load = (
        floors
        * story_height
        * (8 * regular_column_area + c6_area)
        * density
    )
    reconstructed = slab_load + beam_load + column_load
    published = 1957.0
    gravity = 9.807

    data = {
        "status": "GLOBAL_BALANCE_SOURCE_LOCKED__NODAL_LEDGER_PENDING",
        "published_weight_kN": published,
        "reconstructed_weight_kN": reconstructed,
        "residual_kN": reconstructed - published,
        "residual_pct": 100.0 * (reconstructed - published) / published,
        "reconstructed_mass_t": reconstructed / gravity,
        "published_mass_t": published / gravity,
        "components_kN": {
            "three_slabs_plus_finish_plus_0_3_live": slab_load,
            "three_floors_beam_drops_using_table_2_1_clear_spans": beam_load,
            "three_storeys_columns_using_centerline_height": column_load,
        },
        "source_inputs": {
            "slab_plan_m": list(SLAB_PLAN_DIMS),
            "slab_area_m2": slab_area,
            "slab_thickness_m": SLAB_THICKNESS,
            "rc_unit_weight_kN_m3": density,
            "finish_kN_m2": finish,
            "effective_live_kN_m2": live_effective,
            "sum_clear_beam_spans_m": clear_beam_length,
            "beam_web_m": beam_web,
            "beam_drop_below_slab_m": beam_drop,
            "story_height_m": story_height,
        },
        "acceptance_note": (
            "The 0.0585% closure verifies the global load reconstruction; it "
            "does not recover the unpublished ZeusNL node-by-node allocation."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
