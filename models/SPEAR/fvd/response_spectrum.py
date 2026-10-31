"""Linear elastic acceleration response spectra using constant-average Newmark."""
from __future__ import annotations

import math

from ground_motion import GroundMotion


def spectral_acceleration(
    motion: GroundMotion, periods_s: tuple[float, ...], damping_ratio: float = 0.05
) -> tuple[float, ...]:
    """Return pseudo-spectral acceleration (m/s2) for unit-mass SDOFs."""
    if not (0.0 <= damping_ratio < 1.0):
        raise ValueError("damping_ratio must satisfy 0 <= zeta < 1")
    if not motion.values_m_s2:
        raise ValueError("motion is empty")
    dt = motion.dt_s
    beta, gamma = 0.25, 0.5
    result = []
    for period in periods_s:
        if not math.isfinite(period) or period <= 0:
            raise ValueError("periods must be finite and positive")
        omega = 2.0 * math.pi / period
        stiffness = omega * omega
        damping = 2.0 * damping_ratio * omega
        a0 = 1.0 / (beta * dt * dt)
        a1 = gamma / (beta * dt)
        a2 = 1.0 / (beta * dt)
        a3 = 1.0 / (2.0 * beta) - 1.0
        a4 = gamma / beta - 1.0
        a5 = dt * (gamma / (2.0 * beta) - 1.0)
        effective_k = stiffness + a0 + a1 * damping
        displacement = velocity = 0.0
        acceleration = -motion.values_m_s2[0]
        peak_displacement = 0.0
        for ground_acceleration in motion.values_m_s2[1:]:
            load = -ground_acceleration
            effective_load = (
                load
                + a0 * displacement + a2 * velocity + a3 * acceleration
                + damping * (a1 * displacement + a4 * velocity + a5 * acceleration)
            )
            new_displacement = effective_load / effective_k
            new_acceleration = a0 * (new_displacement - displacement) - a2 * velocity - a3 * acceleration
            new_velocity = velocity + dt * ((1.0 - gamma) * acceleration + gamma * new_acceleration)
            displacement, velocity, acceleration = new_displacement, new_velocity, new_acceleration
            peak_displacement = max(peak_displacement, abs(displacement))
        result.append(omega * omega * peak_displacement)
    return tuple(result)
