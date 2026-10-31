"""Ground-motion input with explicit units and deterministic conversion."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import re

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


def read_peer_at2(path: Path, unit: str = "g", scale_factor: float = 1.0) -> GroundMotion:
    """Read a PEER/NGA ``.AT2`` acceleration file without guessing metadata.

    The function requires the standard ``NPTS=..., DT=... SEC`` header and
    verifies that the declared and parsed sample counts agree.
    """
    lines = path.read_text(errors="strict").splitlines()
    header_index = None
    npts = None
    dt_s = None
    pattern = re.compile(
        r"NPTS\s*=\s*(\d+)\s*,?\s*DT\s*=\s*([0-9.Ee+\-]+)\s*SEC",
        re.IGNORECASE,
    )
    for index, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            header_index = index
            npts = int(match.group(1))
            dt_s = float(match.group(2))
            break
    if header_index is None or npts is None or dt_s is None:
        raise ValueError(f"missing PEER NPTS/DT header in {path}")
    if npts <= 0:
        raise ValueError("PEER NPTS must be positive")
    data_text = " ".join(lines[header_index + 1 :]).replace(",", " ")
    try:
        raw = tuple(float(token) for token in data_text.split())
    except ValueError as exc:
        raise ValueError(f"non-numeric PEER acceleration data in {path}") from exc
    if len(raw) != npts:
        raise ValueError(f"PEER NPTS mismatch: header={npts}, parsed={len(raw)}")
    factors = {"g": G_M_S2, "m/s2": 1.0, "cm/s2": 0.01}
    if unit not in factors:
        raise ValueError(f"unsupported acceleration unit: {unit}")
    if not math.isfinite(dt_s) or dt_s <= 0:
        raise ValueError("PEER DT must be finite and positive")
    if not math.isfinite(scale_factor) or scale_factor <= 0:
        raise ValueError("scale_factor must be finite and positive")
    if not all(math.isfinite(value) for value in raw):
        raise ValueError("ground-motion values must be finite")
    factor = factors[unit] * scale_factor
    return GroundMotion(tuple(value * factor for value in raw), dt_s, str(path), unit, scale_factor)

