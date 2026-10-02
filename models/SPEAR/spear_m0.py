"""SPEAR-M0 modal validation driver.

This file deliberately contains the published validation targets and the
acceptance/reporting logic before the full physical model is completed.
It must not fabricate periods: build_spear_m0() raises until the geometry
and connectivity are explicitly locked and implemented.
"""
from dataclasses import dataclass
import csv
import math
from pathlib import Path
import openseespy.opensees as ops

EFCP_TARGETS = (0.559, 0.476, 0.385)
ETCP_REFERENCES = (0.570, 0.484, 0.392)

@dataclass
class ModalResult:
    mode: int
    period_s: float
    efcp_target_s: float
    error_pct: float

def build_spear_m0():
    """Build the physical SPEAR-M0 model.

    Validation guard: do not substitute a generic rectangular frame for the
    published irregular SPEAR connectivity. The exact member map is currently
    being locked from the benchmark drawings.
    """
    raise RuntimeError(
        "SPEAR-M0 geometry/connectivity not yet source-locked. "
        "Model remains NOT VALIDATED; refusing to generate synthetic periods."
    )

def run_modal(n_modes=3):
    build_spear_m0()
    lambdas = ops.eigen("-fullGenLapack", n_modes)
    periods = [2.0 * math.pi / math.sqrt(x) for x in lambdas]
    results = []
    for i, (t, target) in enumerate(zip(periods, EFCP_TARGETS), start=1):
        results.append(ModalResult(i, t, target, 100.0 * (t-target)/target))
    return results

def write_results(results, path="results/modal_results.csv"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode","period_s","efcp_target_s","error_pct"])
        for r in results:
            w.writerow([r.mode, f"{r.period_s:.8f}", r.efcp_target_s, f"{r.error_pct:.3f}"])

if __name__ == "__main__":
    results = run_modal()
    write_results(results)
    for r in results:
        print(f"Mode {r.mode}: T={r.period_s:.6f}s target={r.efcp_target_s:.3f}s error={r.error_pct:+.2f}%")
