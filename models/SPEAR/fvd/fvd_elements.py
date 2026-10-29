"""Validated OpenSees FVD element creation without embedded design choices."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class DamperSpec:
    element_tag: int
    material_tag: int
    node_i: int
    node_j: int
    c_n_s_per_m: float
    alpha: float
    local_direction: int = 1

    def validate(self) -> None:
        if self.element_tag <= 0 or self.material_tag <= 0:
            raise ValueError("OpenSees tags must be positive")
        if self.node_i == self.node_j:
            raise ValueError("damper end nodes must be distinct")
        if not math.isfinite(self.c_n_s_per_m) or self.c_n_s_per_m <= 0:
            raise ValueError("C must be finite and positive in N*(s/m)^alpha")
        if not math.isfinite(self.alpha) or not (0.0 < self.alpha <= 1.0):
            raise ValueError("alpha must satisfy 0 < alpha <= 1")
        if self.local_direction not in (1, 2, 3):
            raise ValueError("local_direction must be 1, 2 or 3")


def add_viscous_damper(ops, spec: DamperSpec) -> None:
    """Add a zero-length nonlinear viscous damper.

    The constitutive law is F=C*|v|^alpha*sign(v). End nodes must already be
    coincident or connected through an explicitly modelled brace geometry.
    """
    spec.validate()
    ops.uniaxialMaterial("Viscous", spec.material_tag, spec.c_n_s_per_m, spec.alpha)
    ops.element(
        "twoNodeLink", spec.element_tag, spec.node_i, spec.node_j,
        "-mat", spec.material_tag, "-dir", spec.local_direction,
    )


def validate_unique_specs(specs: list[DamperSpec]) -> None:
    for spec in specs:
        spec.validate()
    element_tags = [spec.element_tag for spec in specs]
    material_tags = [spec.material_tag for spec in specs]
    if len(element_tags) != len(set(element_tags)):
        raise ValueError("duplicate damper element tags")
    if len(material_tags) != len(set(material_tags)):
        raise ValueError("duplicate damper material tags")

