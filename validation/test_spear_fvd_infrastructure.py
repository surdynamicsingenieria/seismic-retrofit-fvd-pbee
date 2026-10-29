"""Solver-independent tests for FVD inputs and NLTHA unit handling."""
from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FVD = ROOT / "models" / "SPEAR" / "fvd"
sys.path.insert(0, str(FVD))

from fvd_elements import DamperSpec, validate_unique_specs  # noqa: E402
from ground_motion import G_M_S2, read_ground_motion  # noqa: E402
from record_manifest import validate_manifest  # noqa: E402
from run_baseline_nltha import rayleigh_coefficients  # noqa: E402


def expect_error(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


valid = DamperSpec(1, 101, 10, 11, 2.5e6, 0.5)
validate_unique_specs([valid])
expect_error(lambda: DamperSpec(1, 101, 10, 10, 2.5e6, 0.5).validate())
expect_error(lambda: DamperSpec(1, 101, 10, 11, -1.0, 0.5).validate())
expect_error(lambda: DamperSpec(1, 101, 10, 11, 1.0, 1.2).validate())
expect_error(lambda: validate_unique_specs([valid, DamperSpec(1, 102, 12, 13, 1.0, 1.0)]))

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "record.txt"
    path.write_text("0, 0.1, -0.2\n")
    motion = read_ground_motion(path, 0.02, "g", 2.0)
    assert motion.values_m_s2 == (0.0, 0.2 * G_M_S2, -0.4 * G_M_S2)
    assert math.isclose(motion.duration_s, 0.04)

alpha_m, beta_k = rayleigh_coefficients(0.02, (0.51, 0.40))
w1, w2 = 2 * math.pi / 0.51, 2 * math.pi / 0.40
for omega in (w1, w2):
    recovered = 0.5 * (alpha_m / omega + beta_k * omega)
    assert math.isclose(recovered, 0.02, rel_tol=1e-12)

manifest = validate_manifest(ROOT / "validation/fixtures/smoke_record_manifest.json")
assert manifest["suite_id"] == "synthetic-smoke-only"

print("SPEAR_FVD_INFRASTRUCTURE PASS")

