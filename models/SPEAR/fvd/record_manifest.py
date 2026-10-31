"""Strict ground-motion suite manifest validation."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

REQUIRED = ("record_id", "event", "station", "component", "path", "dt_s", "unit",
            "scale_factor", "source_url", "sha256")


def validate_manifest(path: Path, require_files: bool = True) -> dict:
    data = json.loads(path.read_text())
    if not isinstance(data.get("records"), list) or not data["records"]:
        raise ValueError("manifest must contain a non-empty records list")
    ids = set()
    for index, record in enumerate(data["records"]):
        missing = [key for key in REQUIRED if key not in record]
        if missing:
            raise ValueError(f"record {index} missing fields: {missing}")
        if record["record_id"] in ids:
            raise ValueError(f"duplicate record_id: {record['record_id']}")
        ids.add(record["record_id"])
        if record["unit"] not in ("g", "m/s2", "cm/s2"):
            raise ValueError(f"invalid unit for {record['record_id']}")
        if not math.isfinite(record["dt_s"]) or record["dt_s"] <= 0:
            raise ValueError(f"invalid dt_s for {record['record_id']}")
        if not math.isfinite(record["scale_factor"]) or record["scale_factor"] <= 0:
            raise ValueError(f"invalid scale factor for {record['record_id']}")
        record_path = (path.parent / record["path"]).resolve()
        if require_files:
            if not record_path.is_file():
                raise ValueError(f"missing file for {record['record_id']}: {record_path}")
            digest = hashlib.sha256(record_path.read_bytes()).hexdigest()
            if digest != record["sha256"]:
                raise ValueError(f"SHA-256 mismatch for {record['record_id']}")
    return data


def validated_horizontal_pairs(path: Path, require_files: bool = True) -> list[tuple[dict, dict]]:
    """Return manifest records grouped into complete, time-compatible X/Y pairs."""
    data = validate_manifest(path, require_files=require_files)
    groups: dict[str, dict[str, dict]] = {}
    for record in data["records"]:
        pair_id = record.get("pair_id")
        axis = record.get("horizontal_axis")
        if not isinstance(pair_id, str) or not pair_id.strip():
            raise ValueError(f"missing pair_id for {record['record_id']}")
        if axis not in ("X", "Y"):
            raise ValueError(f"horizontal_axis must be X or Y for {record['record_id']}")
        if axis in groups.setdefault(pair_id, {}):
            raise ValueError(f"duplicate {axis} component for pair {pair_id}")
        groups[pair_id][axis] = record
    pairs = []
    for pair_id, components in groups.items():
        if set(components) != {"X", "Y"}:
            raise ValueError(f"pair {pair_id} must contain exactly X and Y components")
        x, y = components["X"], components["Y"]
        if not math.isclose(x["dt_s"], y["dt_s"], rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"time-step mismatch in pair {pair_id}")
        pairs.append((x, y))
    return pairs

