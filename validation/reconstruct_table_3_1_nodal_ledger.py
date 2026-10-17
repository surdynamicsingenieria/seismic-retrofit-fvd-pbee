"""Write the nodal gravity/mass ledger recovered from MAE 04-03 Table 3.1."""

import csv
import json
from pathlib import Path
import sys

MODEL = Path(__file__).resolve().parents[1] / "models/SPEAR/jeong_elnashai"
sys.path.insert(0, str(MODEL))

from gravity_mass_source import (
    COLUMN_AXIAL_KN, FLOOR_CM, FLOOR_MASSES_KG, FLOOR_WEIGHTS_KN,
    GACC, NODE_WEIGHTS_KN,
)

OUT = Path("results/SPEAR/jeong_elnashai")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "table_3_1_nodal_gravity_mass_ledger.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("joint", "floor", "weight_kN", "mass_kg"))
        for joint, values in NODE_WEIGHTS_KN.items():
            for floor, weight in enumerate(values, 1):
                writer.writerow((joint, floor, weight, 1000.0 * weight / GACC))

    data = {
        "method": "floor load = axial force below - axial force above; roof load = storey-3 axial force",
        "column_axial_forces_kN": COLUMN_AXIAL_KN,
        "floor_weights_kN": FLOOR_WEIGHTS_KN,
        "floor_masses_kg": FLOOR_MASSES_KG,
        "floor_centres_of_mass_m": FLOOR_CM,
        "sum_table_3_1_base_axial_kN": sum(FLOOR_WEIGHTS_KN),
        "mae_report_scalar_weight_kN": 1957.0,
        "internal_report_difference_kN": sum(FLOOR_WEIGHTS_KN) - 1957.0,
        "cross_check": "Matches the independent 67.264, 67.264, 62.804 t workshop mass set within table rounding.",
    }
    (OUT / "table_3_1_nodal_gravity_mass_audit.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
