"""Ground-motion input with explicit units and deterministic conversion."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

G_M_S2 = 9.80665


@dataclass(frozen=True)
class GroundMotion:
    values_m_s2: tuple[float, ...]
    dt_s: float
    source: str
    original_unit: str
    scale_factor: float

    @property
    def duration_s(self) -> float:
        return (len(self.values_m_s2) - 1) * self.dt_s

    @property
    def pga_m_s2(self) -> float:
        return max(abs(value) for value in self.values_m_s2)


def read_ground_motion(path: Path, dt_s: float, unit: str, scale_factor: float = 1.0) -> GroundMotion:
    if not math.isfinite(dt_s) or dt_s <= 0:
        raise ValueError("dt_s must be finite and positive")
    if not math.isfinite(scale_factor) or scale_factor <= 0:
        raise ValueError("scale_factor must be finite and positive")
    factors = {"g": G_M_S2, "m/s2": 1.0, "cm/s2": 0.01}
    if unit not in factors:
        raise ValueError(f"unsupported acceleration unit: {unit}")
    tokens = path.read_text().replace(",", " ").split()
    if not tokens:
        raise ValueError("ground-motion file is empty")
    raw = tuple(float(token) for token in tokens)
    if not all(math.isfinite(value) for value in raw):
        raise ValueError("ground-motion values must be finite")
    factor = factors[unit] * scale_factor
    return GroundMotion(tuple(value * factor for value in raw), dt_s, str(path), unit, scale_factor)

