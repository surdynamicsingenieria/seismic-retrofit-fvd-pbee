"""Source-locked lateral load patterns for Jeong-Elnashai SPEAR pushover.

MAE 04-03, Section 2.3.1 states that equivalent lateral force distribution is
proportional to the first mode shape and mass distribution (Eq. 2.5). The force
on each floor is then redistributed to loading points/frames in proportion to
supported mass, as shown in Fig. 2.7.

This module deliberately does not choose modes by modal effective mass. The
first mode shape vector must be supplied by the model that is being pushed.
"""

from __future__ import annotations

REQUIRED_PATTERNS = ("xp100", "xn100", "yp100", "yn100")

# Fig. 2.7: plan distribution of equivalent lateral load.
X_FRAME_FRACTIONS = (0.24, 0.50, 0.26)
Y_FRAME_FRACTIONS = (0.15, 0.44, 0.41)


def floor_force_fractions(first_mode_shape: list[float], floor_masses: list[float]) -> list[float]:
    """Return Eq. 2.5 floor fractions from first mode shape and floor masses."""
    if len(first_mode_shape) != len(floor_masses):
        raise ValueError("first_mode_shape and floor_masses must have the same length")
    weighted = [abs(phi) * mass for phi, mass in zip(first_mode_shape, floor_masses)]
    total = sum(weighted)
    if total <= 0.0:
        raise ValueError("first-mode mass weighting must be positive")
    return [value / total for value in weighted]


def get_pattern(name: str, first_mode_shape: list[float], floor_masses: list[float]) -> list[list[float]]:
    """Build normalized nodal/frame load fractions for a published pushover case.

    Returns one row per floor. Each row contains three frame/loading-point
    fractions for that floor. The sign encodes the loading direction.
    """
    if name not in REQUIRED_PATTERNS:
        raise ValueError(f"Unknown Jeong-Elnashai pushover pattern: {name}")

    floor_fracs = floor_force_fractions(first_mode_shape, floor_masses)
    if name.startswith("x"):
        frame_fracs = X_FRAME_FRACTIONS
    else:
        frame_fracs = Y_FRAME_FRACTIONS
    sign = -1.0 if name[1] == "n" else 1.0
    return [[sign * floor_frac * frame_frac for frame_frac in frame_fracs] for floor_frac in floor_fracs]
