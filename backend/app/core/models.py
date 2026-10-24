from dataclasses import dataclass


@dataclass(frozen=True)
class SoilParams:
    """Parámetros de suelo (talud homogéneo, fase 1)."""
    cohesion: float          # kPa
    phi: float               # grados (nunca radianes)
    gamma: float             # kN/m³
    ru: float = 0.0          # relación de presión de poros (adimensional)


@dataclass(frozen=True)
class SlopeGeometry:
    """Geometría del talud. Pie en (0,0), cara recta hasta la cresta."""
    height: float            # m
    angle: float             # grados (cara del talud desde la horizontal)


@dataclass(frozen=True)
class SlipCircle:
    """Círculo de falla. El arco de falla es la porción inferior."""
    center_x: float          # m
    center_y: float          # m
    radius: float            # m


@dataclass(frozen=True)
class Slice:
    """Dovela. weight (W) se deriva: W = gamma * width * height."""
    width: float             # b, m (horizontal)
    height: float            # h, m (punto medio: base → superficie)
    base_angle: float        # α, grados, positivo hacia abajo


@dataclass(frozen=True)
class BishopResult:
    fs: float
    iterations: int
    converged: bool
