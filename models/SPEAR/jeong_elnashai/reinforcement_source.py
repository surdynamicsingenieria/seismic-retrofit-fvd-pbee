"""Source-locked reinforcement data from MAE 04-03 Fig. 2.3.

The report gives typical member sections and a typical beam longitudinal layout.
It does not provide a member-by-member reinforcement schedule in tabular form.
Do not extend this module with inferred reinforcement variants.
"""

from __future__ import annotations

import math

COVER_M = 0.015

BAR_DIAMETER_M = {
    "phi8": 0.008,
    "phi12": 0.012,
    "phi20": 0.020,
}

STEEL_PROPERTIES = {
    "phi8": {"fy_mpa": 467.0, "fu_mpa": 583.67, "ey": 0.00227, "eu": 0.131, "es_mpa": 206000.0, "e2_over_e1": 0.0044},
    "phi12": {"fy_mpa": 458.67, "fu_mpa": 570.33, "ey": 0.00223, "eu": 0.174, "es_mpa": 206000.0, "e2_over_e1": 0.0032},
    "phi20": {"fy_mpa": 376.67, "fu_mpa": 567.33, "ey": 0.00183, "eu": 0.168, "es_mpa": 206000.0, "e2_over_e1": 0.0056},
}

COLUMN_REINFORCEMENT = {
    "regular": {"section_m": (0.25, 0.25), "longitudinal": "4phi12", "stirrups": "phi8@0.25m"},
    "C6": {"section_m": (0.75, 0.25), "longitudinal": "10phi12", "stirrups": "phi8@0.25m"},
}

TYPICAL_BEAM_REINFORCEMENT = {
    "section_m": (0.25, 0.50),
    "slab_thickness_m": 0.15,
    "top_bars_at_section_A": "2phi12",
    "bottom_bars_at_section_A": "4phi12",
    "bent_bottom_bars_at_beam_ends": "2phi12",
    "stirrups": "phi8@0.20m",
}


def bar_area_m2(bar_name: str) -> float:
    diameter = BAR_DIAMETER_M[bar_name]
    return math.pi * diameter**2 / 4.0
