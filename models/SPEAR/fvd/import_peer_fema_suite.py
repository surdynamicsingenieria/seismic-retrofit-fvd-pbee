"""Import an authenticated PEER package without redistributing waveforms."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

from ground_motion import read_peer_at2


def run(source: Path, ledger: Path, output: Path) -> None:
    rows = list(csv.DictReader(ledger.open()))
    records, missing = [], []
    for row in rows:
        rsn = row["rsn"]
        components = []
        for axis, key in (("X", "h1_filename"), ("Y", "h2_filename")):
            base = Path(row[key]).name
            candidates = list(source.glob(f"RSN{rsn}_*{base}"))
            if len(candidates) != 1:
                components = []
                break
            path = candidates[0]
            motion = read_peer_at2(path)
            header = path.read_text(errors="strict").splitlines()
            description = [part.strip() for part in header[1].split(",")]
            components.append({
                "record_id": f"RSN{rsn}-{axis}",
                "pair_id": f"RSN{rsn}",
                "horizontal_axis": axis,
                "event": description[0],
                "station": description[2],
                "component": description[-1],
                "path": os.path.relpath(path.resolve(), output.parent.resolve()),
                "dt_s": motion.dt_s,
                "unit": "g",
                "scale_factor": 1.0,
                "source_url": "https://ngawest2.berkeley.edu/",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "npts": len(motion.values_m_s2),
                "pga_g": motion.pga_m_s2 / 9.80665,
            })
        if components:
            records.extend(components)
        else:
            missing.append(int(rsn))
    data = {
        "suite": "FEMA P-695 far-field set",
        "provenance": "PEER NGA-West2 authenticated unscaled as-recorded package",
        "expected_pairs": len(rows),
        "available_pairs": len(records) // 2,
        "missing_rsns": missing,
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({k: data[k] for k in ("expected_pairs", "available_pairs", "missing_rsns")}, indent=2))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("--ledger", type=Path, default=Path(__file__).with_name("fema_p695_far_field_suite.csv"))
    p.add_argument("--output", type=Path, required=True)
    return p


if __name__ == "__main__":
    args = parser().parse_args()
    run(args.source, args.ledger, args.output)
