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
from ground_motion import G_M_S2, GroundMotion, read_ground_motion, read_peer_at2  # noqa: E402
from record_manifest import validate_manifest, validated_horizontal_pairs  # noqa: E402
from response_spectrum import spectral_acceleration  # noqa: E402
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
pairs = validated_horizontal_pairs(ROOT / "validation/fixtures/smoke_record_manifest.json")
assert len(pairs) == 1 and pairs[0][0]["horizontal_axis"] == "X" and pairs[0][1]["horizontal_axis"] == "Y"

peer_motion = read_peer_at2(ROOT / "validation/fixtures/synthetic_peer_sine.AT2")
assert len(peer_motion.values_m_s2) == 21
assert math.isclose(peer_motion.dt_s, 0.02)
assert math.isclose(peer_motion.pga_m_s2, 0.05 * G_M_S2)

# For a long harmonic input at resonance, the 5%-damped pseudo-acceleration
# approaches approximately PGA/(2*zeta). Use a finite-duration tolerance to
# catch formulation/unit regressions without treating the fixture as research data.
period = 0.4
samples = tuple(0.05 * G_M_S2 * math.sin(2 * math.pi * i * 0.002 / period) for i in range(10001))
harmonic = GroundMotion(samples, 0.002, "analytic-test", "m/s2", 1.0)
sa = spectral_acceleration(harmonic, (period,), 0.05)[0]
assert math.isclose(sa, 0.05 * G_M_S2 / 0.1, rel_tol=0.03)

print("SPEAR_FVD_INFRASTRUCTURE PASS")

