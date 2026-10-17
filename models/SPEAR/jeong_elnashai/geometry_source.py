"""Source-locked geometry for SPEAR Jeong-Elnashai MAE 04-03.

Coordinates are reconstructed directly from Fig. 2.2 dimension chains (metres).
No modal calibration is embedded here.
"""
JOINTS = {
    "C8": (0.0, 0.0), "C6": (3.0, 0.25), "C7": (9.0, 0.5),
    "C9": (0.0, 5.0), "C3": (3.0, 4.5), "C4": (9.0, 4.5),
    "C5": (0.0, 10.5), "C1": (3.0, 10.5), "C2": (8.0, 10.5),
}
STORY_CENTERLINES = (0.0, 3.0, 6.0, 9.0)
SLAB_THICKNESS = 0.150
# Fig. 2.2 slab outline.  The framing lines do not coincide with every slab
# edge: the right-hand cantilever is dimensioned 1.0 + 0.7 m beyond C2 and the
# full plan dimensions are 9.7 x 10.5 m.
SLAB_PLAN_DIMS = (9.70, 10.50)
COLUMN = {"regular": (.250, .250), "C6": (.750, .250)}
BEAMS = [
    ("B1", "C5", "C1"), ("B2", "C1", "C2"), ("B3", "C9", "C3"), ("B4", "C3", "C4"),
    ("B5", "C8", "C6"), ("B6", "C6", "C7"), ("B7", "C2", "C4"), ("B8", "C4", "C7"),
    ("B9", "C1", "C3"), ("B10", "C3", "C6"), ("B11", "C5", "C9"), ("B12", "C9", "C8"),
]
CLEAR_SPAN_MM = {
    "B1": 2750, "B2": 4750, "B3": 2750, "B4": 5750, "B5": 2750, "B6": 5750,
    "B7": 5750, "B8": 3750, "B9": 5750, "B10": 3750, "B11": 5250, "B12": 4750,
}
BEFF_MM = {
    "B1": 442.5, "B2": 582.5, "B3": 635.0, "B4": 1055.0, "B5": 442.5, "B6": 652.5,
    "B7": 1055.0, "B8": 775.0, "B9": 1055.0, "B10": 775.0, "B11": 617.5, "B12": 582.5,
}
