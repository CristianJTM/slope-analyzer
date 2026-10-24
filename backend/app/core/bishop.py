import math

from .models import BishopResult, Slice, SoilParams


def bishop_fs(
    slices: list[Slice],
    soil: SoilParams,
    *,
    tolerance: float = 1e-4,
    max_iterations: int = 100,
) -> BishopResult:
    """Factor de seguridad por Bishop Simplificado (método de las dovelas).

    FS = Σ [ (cohesion·b_i + W_i·(1 − ru)·tan φ) / m_α,i ] / Σ [ W_i·sin α_i ]

      W_i   = gamma · width_i · height_i
      m_α,i = cos α_i · (1 + tan α_i · tan φ / FS)

    φ y α se usan en grados y se convierten a radianes internamente.
    Iteración desde FS₀ = 1.0 hasta |ΔFS| < tolerance o max_iterations.
    Devuelve converged=False si no converge en ese límite.

    Lanza ValueError si slices está vacío, si algún width/height < 0, o si
    gamma <= 0 / cohesion < 0 / phi < 0.
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
    cosines: list[float] = []
    sines: list[float] = []
    numerator_terms: list[float] = []
    denominator = 0.0
    for s in slices:
        alpha = math.radians(s.base_angle)
        cos_a = math.cos(alpha)
        sin_a = math.sin(alpha)
        weight = soil.gamma * s.width * s.height
        numerator_terms.append(
            soil.cohesion * s.width + weight * (1.0 - soil.ru) * tan_phi
        )
        cosines.append(cos_a)
        sines.append(sin_a)
        denominator += weight * sin_a

    if denominator == 0.0:
        total = sum(numerator_terms)
        fs = 0.0 if total == 0.0 else math.inf
        return BishopResult(fs=fs, iterations=0, converged=True)

    fs = 1.0
    for iteration in range(1, max_iterations + 1):
        numerator = 0.0
        for term, cos_a, sin_a in zip(numerator_terms, cosines, sines):
            m_alpha = cos_a if tan_phi == 0.0 else cos_a + sin_a * tan_phi / fs
            numerator += term / m_alpha
        new_fs = numerator / denominator
        if abs(new_fs - fs) < tolerance:
            return BishopResult(fs=new_fs, iterations=iteration, converged=True)
        fs = new_fs
    return BishopResult(fs=fs, iterations=max_iterations, converged=False)
