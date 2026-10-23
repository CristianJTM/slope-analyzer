# Bishop Core — Especificación (Fase 1)

Analizador de estabilidad de taludes. Módulo de cálculo **Bishop Simplificado**
en Python puro, sin FastAPI. Todo vive en `backend/app/core/` y es testeable
sin levantar servidor.

## Estado

- [x] Interfaz pública cerrada
- [x] Tests T1, T2, T4 definidos (verificados a mano)
- [ ] T3 pendiente: geometría/círculo/FS de **Hyrcan** (placeholders `TODO`)

## Glosario (convenciones de nombres)

| Término | Significado |
|---|---|
| `fs` | factor de seguridad (nunca `safety_factor`/`sf`) |
| `slice` | dovela |
| `slip_circle` | círculo de falla |
| `cohesion` | cohesión del suelo (kPa) |
| `phi` | ángulo de fricción interna (**grados**) |
| `gamma` | peso unitario del suelo (kN/m³) |

`phi`, `angle` y `base_angle` se expresan **siempre en grados** en la interfaz
pública. Nunca radianes ni ratio H:V.

## Convenciones de coordenadas

- Origen `(0, 0)` = pie del talud (toe).
- `x` → hacia la cresta (entrando al talud); `y` → vertical hacia arriba.
- Cara del talud: recta `(0,0) → (height/tan(angle), height)`.
  Cresta horizontal en `y=height` para `x ≥ height/tan(angle)`.
  Base horizontal en `y=0` para `x ≤ 0`.
- Círculo de falla: centro `(cx, cy)` + radio `R`. El arco de falla es la
  porción **inferior**, saliendo en el pie y en la cresta.
- `base_angle` (α): ángulo de la tangente al arco con la horizontal,
  positivo hacia abajo (dirección del deslizamiento).

## Modelo de datos — `backend/app/core/models.py`

```python
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
```

## Funciones

### `backend/app/core/slicing.py`

```python
from .models import SlopeGeometry, SlipCircle, Slice


def slice_slope(
    geometry: SlopeGeometry,
    slip_circle: SlipCircle,
    num_slices: int = 10,
) -> list[Slice]:
    """Divide la masa deslizante en `num_slices` dovelas verticales.

    El arco de falla es la porción inferior del círculo, entre sus dos
    intersecciones con la superficie del terreno.

    Lanza ValueError si height ≤ 0, num_slices < 1, o el círculo no corta el
    terreno en dos puntos.
    """
    ...
```

### `backend/app/core/bishop.py`

```python
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
    gamma ≤ 0 / cohesion < 0 / phi < 0.
    """
    ...
```

## Tests — `backend/tests/`

### `test_bishop.py`

```python
import pytest

from app.core.bishop import bishop_fs
from app.core.models import Slice, SoilParams


def _two_slices() -> list[Slice]:
    return [
        Slice(width=2.0, height=3.0, base_angle=20.0),
        Slice(width=2.0, height=3.0, base_angle=20.0),
    ]


def test_friction_only_hand_verified():
    # T1: solo fricción, sin agua. FS esperado calculado a mano ≈ 1.586.
    soil = SoilParams(cohesion=0.0, phi=30.0, gamma=20.0, ru=0.0)
    result = bishop_fs(_two_slices(), soil)
    assert result.converged
    assert result.fs == pytest.approx(1.586, abs=1e-3)


def test_cohesion_and_ru_hand_verified():
    # T2: con cohesión y presión de poros. FS esperado ≈ 1.437.
    soil = SoilParams(cohesion=10.0, phi=25.0, gamma=20.0, ru=0.25)
    result = bishop_fs(_two_slices(), soil)
    assert result.converged
    assert result.fs == pytest.approx(1.437, abs=1e-3)


def test_no_strength_gives_zero_fs():
    # c=0 y φ=0 ⇒ sin resistencia, FS = 0.
    slices = [Slice(width=2.0, height=3.0, base_angle=20.0)]
    soil = SoilParams(cohesion=0.0, phi=0.0, gamma=20.0, ru=0.0)
    result = bishop_fs(slices, soil)
    assert result.fs == pytest.approx(0.0, abs=1e-9)


def test_empty_slices_raises():
    with pytest.raises(ValueError):
        bishop_fs([], SoilParams(cohesion=10.0, phi=30.0, gamma=20.0))
```

### `test_slicing.py`

```python
import pytest

from app.core.bishop import bishop_fs
from app.core.models import SlipCircle, SlopeGeometry, SoilParams
from app.core.slicing import slice_slope


def test_vertical_slope_does_not_crash():
    # Talud vertical (β=90°) no debe romper; círculo que pasa por el pie (0,0).
    geometry = SlopeGeometry(height=10.0, angle=90.0)
    circle = SlipCircle(center_x=5.0, center_y=12.0, radius=13.0)
    slices = slice_slope(geometry, circle, num_slices=10)
    assert len(slices) == 10
    assert all(s.height >= 0 for s in slices)


# TODO: reemplazar con valores de hyrcan
HYRCAN_HEIGHT = 0.0         # m
HYRCAN_ANGLE = 0.0          # grados
HYRCAN_COHESION = 0.0       # kPa
HYRCAN_PHI = 0.0            # grados
HYRCAN_GAMMA = 0.0          # kN/m³
HYRCAN_RU = 0.0             # adimensional
HYRCAN_CIRCLE = SlipCircle(center_x=0.0, center_y=0.0, radius=0.0)  # m
HYRCAN_EXPECTED_FS = 0.0    # FS reportado por hyrcan
HYRCAN_NUM_SLICES = 20


@pytest.mark.skip(reason="TODO: completar con geometría/círculo de hyrcan")
def test_hyrcan_benchmark():
    # T3: end-to-end (slice_slope + bishop_fs) contra Hyrcan.
    geometry = SlopeGeometry(height=HYRCAN_HEIGHT, angle=HYRCAN_ANGLE)
    soil = SoilParams(
        cohesion=HYRCAN_COHESION,
        phi=HYRCAN_PHI,
        gamma=HYRCAN_GAMMA,
        ru=HYRCAN_RU,
    )
    slices = slice_slope(geometry, HYRCAN_CIRCLE, num_slices=HYRCAN_NUM_SLICES)
    result = bishop_fs(slices, soil)
    assert result.fs == pytest.approx(HYRCAN_EXPECTED_FS, rel=2e-2)  # ±2%
```

## Layout y ejecución

```
backend/app/core/__init__.py   # vacío
backend/app/core/models.py
backend/app/core/slicing.py
backend/app/core/bishop.py
backend/tests/test_bishop.py
backend/tests/test_slicing.py
```

Correr con `pytest` desde `backend/`. Sin dependencias nuevas (solo `pytest`
como dev-dependency).

## Fuera de alcance (fase 1)

- Búsqueda del círculo crítico (minimizar FS variando el círculo).
- Estratigrafía / napa: hoy suelo homogéneo (`SoilParams`) y `ru` global.
  Upgrade futuro: `ru`/`cohesion`/`phi`/`gamma` por dovela, derivados de capas
  y nivel freático. La firma `bishop_fs(slices, soil)` no cambia.
- FastAPI / Pydantic (`core/` queda Python puro).