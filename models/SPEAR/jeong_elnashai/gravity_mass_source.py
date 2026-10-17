"""Source-locked gravity and nodal mass ledger from MAE 04-03 Table 3.1."""

from geometry_source import JOINTS

GACC = 9.807

COLUMN_AXIAL_KN = {
    "C1": (234.22, 154.46, 74.98), "C2": (252.67, 166.54, 80.13),
    "C3": (407.26, 272.34, 139.62), "C4": (328.72, 217.96, 107.89),
    "C5": (89.56, 57.42, 25.43), "C6": (216.44, 141.29, 64.29),
    "C7": (150.45, 98.51, 45.90), "C8": (73.66, 45.72, 18.66),
    "C9": (182.26, 121.37, 59.05),
}

# Load entering each column at floors 1, 2 and roof, respectively.
NODE_WEIGHTS_KN = {
    name: (p1 - p2, p2 - p3, p3)
    for name, (p1, p2, p3) in COLUMN_AXIAL_KN.items()
}
FLOOR_WEIGHTS_KN = tuple(
    sum(values[k] for values in NODE_WEIGHTS_KN.values()) for k in range(3)
)
FLOOR_MASSES_KG = tuple(1000.0 * w / GACC for w in FLOOR_WEIGHTS_KN)


def _centres():
    result = []
    for k, total in enumerate(FLOOR_WEIGHTS_KN):
        x = sum(NODE_WEIGHTS_KN[n][k] * JOINTS[n][0] for n in JOINTS) / total
        y = sum(NODE_WEIGHTS_KN[n][k] * JOINTS[n][1] for n in JOINTS) / total
        result.append((x, y))
    return tuple(result)


FLOOR_CM = _centres()
