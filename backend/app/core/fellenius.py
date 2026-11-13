import math

from .models import Slice, SoilParams


def fellenius_fs(slices: list[Slice], soil: SoilParams) -> float:
    """Factor de seguridad por Fellenius (método ordinario de las dovelas).

    FS = Σ [ cohesion·Δl_i + W_i·(1 − ru)·cos α_i·tan φ ] / Σ [ W_i·sin α_i ]

      W_i  = gamma · width_i · height_i
      Δl_i = width_i / cos α_i          (longitud de la base de la dovela)

    El término W·(1 − ru) es el peso efectivo: misma convención de ru que
    Bishop. A diferencia de Bishop, no itera.
    φ y α se usan en grados y se convierten a radianes internamente.

    Lanza ValueError si slices está vacío, si algún width/height < 0, si
    gamma <= 0 / cohesion < 0 / phi < 0, o si algún base_angle es ±90°.
    """
    if not slices:
        raise ValueError("slices no puede estar vacío")
    for s in slices:
        if s.width < 0 or s.height < 0:
            raise ValueError("width y height de las dovelas deben ser >= 0")
    if soil.gamma <= 0:
        raise ValueError("gamma debe ser > 0")
    if soil.cohesion < 0:
        raise ValueError("cohesion debe ser >= 0")
    if soil.phi < 0:
        raise ValueError("phi debe ser >= 0")

    tan_phi = math.tan(math.radians(soil.phi))
    numerator = 0.0
    denominator = 0.0
    for s in slices:
        alpha = math.radians(s.base_angle)
        cos_a = math.cos(alpha)
        if cos_a == 0.0:
            raise ValueError("base_angle no puede ser ±90°")
        weight = soil.gamma * s.width * s.height
        base_length = s.width / cos_a
        numerator += (
            soil.cohesion * base_length
            + weight * (1.0 - soil.ru) * cos_a * tan_phi
        )
        denominator += weight * math.sin(alpha)

    if denominator == 0.0:
        return 0.0 if numerator == 0.0 else math.inf
    return numerator / denominator
