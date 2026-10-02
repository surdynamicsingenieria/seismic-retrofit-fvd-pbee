"""Minimal OpenSeesPy smoke test for CI.

Builds a one-degree-of-freedom elastic oscillator and checks its
eigenperiod against the analytical solution.
"""
import math
import openseespy.opensees as ops

MASS = 2.0
STIFFNESS = 200.0
EXPECTED_T = 2.0 * math.pi * math.sqrt(MASS / STIFFNESS)

ops.wipe()
ops.model("basic", "-ndm", 1, "-ndf", 1)
ops.node(1, 0.0)
ops.node(2, 1.0)
ops.fix(1, 1)
ops.mass(2, MASS)
ops.uniaxialMaterial("Elastic", 1, STIFFNESS)
ops.element("zeroLength", 1, 1, 2, "-mat", 1, "-dir", 1)

eigenvalue = ops.eigen("-fullGenLapack", 1)[0]
period = 2.0 * math.pi / math.sqrt(eigenvalue)
error = abs(period - EXPECTED_T)

print(f"OpenSeesPy smoke test: T={period:.10f} s; expected={EXPECTED_T:.10f} s")
assert error < 1e-8, f"Eigenperiod mismatch: {error}"
print("SMOKE TEST PASSED")
ops.wipe()
