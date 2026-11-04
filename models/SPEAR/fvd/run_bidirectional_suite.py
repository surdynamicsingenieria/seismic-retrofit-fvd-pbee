"""Run every pair in a validated manifest and aggregate completion/EDP data."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import subprocess
import sys

from record_manifest import validated_horizontal_pairs


def run_one(driver: Path, manifest: Path, output_dir: Path, pair_id: str,
            damping: float, member_formulation: str, retry_incomplete: bool) -> dict:
    output = output_dir / f"{pair_id}.csv"
    log = output_dir / f"{pair_id}.log"
    summary_path = output.with_suffix(".json")
    if output.is_file() and summary_path.is_file():
        existing = json.loads(summary_path.read_text())
        same_setup = (existing.get("damping_ratio") == damping and
                      existing.get("member_formulation", "source_mesh") == member_formulation)
        reusable = existing.get("status") == "COMPLETE" or not retry_incomplete
        if same_setup and reusable:
            existing["process_return_code"] = 0
            existing["log"] = log.name
            return existing
    command = [sys.executable, str(driver), str(manifest), "--pair-id", pair_id,
               "--damping-ratio", str(damping),
               "--member-formulation", member_formulation,
               "--output", str(output)]
    env = os.environ.copy()
    env.setdefault("MPICH_INTERFACE_HOSTNAME", "127.0.0.1")
    env.setdefault("MPIR_CVAR_CH3_INTERFACE_HOSTNAME", "127.0.0.1")
    with log.open("w") as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, env=env)
    summary = json.loads(summary_path.read_text()) if summary_path.is_file() else {
        "status": "NO_SUMMARY", "pair_id": pair_id
    }
    summary["process_return_code"] = result.returncode
    summary["log"] = log.name
    return summary


def main(args) -> int:
    pairs = validated_horizontal_pairs(args.manifest)
    pair_ids = [x["pair_id"] for x, _ in pairs]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    driver = Path(__file__).with_name("run_bidirectional_nltha.py")
    summaries = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, driver, args.manifest.resolve(),
                               args.output_dir.resolve(), pair_id,
                               args.damping_ratio, args.member_formulation,
                               args.retry_incomplete): pair_id for pair_id in pair_ids}
        for future in as_completed(futures):
            summary = future.result()
            summaries.append(summary)
            print(f"{summary['pair_id']}: {summary['status']}", flush=True)
    summaries.sort(key=lambda item: int(item["pair_id"].removeprefix("RSN")))
    aggregate = {
        "suite_label": args.suite_label,
        "manifest": str(args.manifest),
        "damping_ratio": args.damping_ratio,
        "member_formulation": args.member_formulation,
        "requested_pairs": len(pair_ids),
        "complete_pairs": sum(s.get("status") == "COMPLETE" for s in summaries),
        "incomplete_pairs": [s["pair_id"] for s in summaries if s.get("status") != "COMPLETE"],
        "results": summaries,
    }
    (args.output_dir / "suite_summary.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return 0 if aggregate["complete_pairs"] == len(pair_ids) else 3


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--suite-label", default="FEMA-P695-partial-21")
    p.add_argument("--damping-ratio", type=float, default=0.05)
    p.add_argument("--member-formulation", choices=("source_mesh", "hinge_midpoint"),
                   default="source_mesh")
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--retry-incomplete", action="store_true",
                   help="rerun cases with an existing INCOMPLETE summary")
    return p


if __name__ == "__main__":
    raise SystemExit(main(parser().parse_args()))
