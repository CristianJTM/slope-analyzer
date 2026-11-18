import math
from dataclasses import dataclass

from .bishop import bishop_fs
from .fellenius import fellenius_fs
from .models import SlipCircle, SlopeGeometry, SoilParams
from .slicing import slice_slope


@dataclass(frozen=True)
class SearchBounds:
    x_min: float
    x_max: float
    y_min: float
    y_max: float


@dataclass(frozen=True)
class CriticalCircle:
    fs: float
    slip_circle: SlipCircle
    method: str
    num_slices: int
    evaluations: int


def _default_bounds(geometry: SlopeGeometry) -> SearchBounds:
    height = geometry.height
    tan_angle = math.tan(math.radians(geometry.angle))
    crest_x = height / tan_angle if tan_angle > 0 else 0.0
    scale = crest_x if crest_x > 0 else height
    return SearchBounds(
        x_min=-0.5 * scale,
        x_max=1.5 * scale,
        y_min=height,
        y_max=3.0 * height,
    )


def _linspace(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + i * step for i in range(count)]


def _candidate_circles(
    center_x: float, center_y: float, depths: tuple[float, ...]
) -> list[SlipCircle]:
    # Por el pie (0,0): el radio es la distancia del centro al pie.
    circles = [SlipCircle(center_x, center_y, math.hypot(center_x, center_y))]
    # Profundo: tangente a la horizontal y = -depth.
    for depth in depths:
        circles.append(SlipCircle(center_x, center_y, center_y + depth))
    return circles


def _factor_of_safety(slices, soil: SoilParams, method: str) -> float:
    if method == "bishop":
        return bishop_fs(slices, soil).fs
    if method == "fellenius":
        return fellenius_fs(slices, soil)
    raise ValueError(f"método desconocido: {method}")


def _search_grid(
    geometry: SlopeGeometry,
    soil: SoilParams,
    method: str,
    bounds: SearchBounds,
    grid: int,
    depths: tuple[float, ...],
    num_slices: int,
) -> tuple[tuple[float, SlipCircle] | None, int]:
    best: tuple[float, SlipCircle] | None = None
    evaluations = 0
    for center_x in _linspace(bounds.x_min, bounds.x_max, grid):
        for center_y in _linspace(bounds.y_min, bounds.y_max, grid):
            for circle in _candidate_circles(center_x, center_y, depths):
                try:
                    slices = slice_slope(geometry, circle, num_slices=num_slices)
                    fs = _factor_of_safety(slices, soil, method)
                except (ValueError, ZeroDivisionError):
                    continue
                if not math.isfinite(fs):
                    continue
                evaluations += 1
                if best is None or fs < best[0]:
                    best = (fs, circle)
    return best, evaluations


def critical_circle(
    geometry: SlopeGeometry,
    soil: SoilParams,
    method: str = "bishop",
    *,
    bounds: SearchBounds | None = None,
    grid: int = 15,
    depths: tuple[float, ...] = (0.0,),
    num_slices: int = 50,
) -> CriticalCircle:
    """Busca el círculo de falla con FS mínimo (método indicado).

    Candidatos: para cada centro de un grid (xc, yc), un círculo que pasa por
    el pie y círculos profundos tangentes a y = -d para cada d en `depths`.
    Se hace un grid grueso y un refinamiento local alrededor del mejor centro.

    Lanza ValueError si no hay ningún círculo válido en la región.
    """
    if method not in ("bishop", "fellenius"):
        raise ValueError(f"método desconocido: {method}")
    if geometry.height <= 0:
        raise ValueError("height debe ser > 0")
    if grid < 2:
        raise ValueError("grid debe ser >= 2")
    if num_slices < 1:
        raise ValueError("num_slices debe ser >= 1")

    if bounds is None:
        bounds = _default_bounds(geometry)
    if bounds.x_min >= bounds.x_max or bounds.y_min >= bounds.y_max:
        raise ValueError("bounds inválidos: se requiere x_min < x_max e y_min < y_max")

    best, evaluations = _search_grid(
        geometry, soil, method, bounds, grid, depths, num_slices
    )
    if best is None:
        raise ValueError(
            "no se encontró ningún círculo de falla válido en la región de búsqueda"
        )

    best_fs, best_circle = best
    step_x = (bounds.x_max - bounds.x_min) / (grid - 1)
    step_y = (bounds.y_max - bounds.y_min) / (grid - 1)
    refined_bounds = SearchBounds(
        x_min=best_circle.center_x - step_x,
        x_max=best_circle.center_x + step_x,
        y_min=best_circle.center_y - step_y,
        y_max=best_circle.center_y + step_y,
    )
    refined, refined_evaluations = _search_grid(
        geometry, soil, method, refined_bounds, grid, depths, num_slices
    )
    evaluations += refined_evaluations
    if refined is not None and refined[0] <= best_fs:
        best_fs, best_circle = refined

    return CriticalCircle(
        fs=best_fs,
        slip_circle=best_circle,
        method=method,
        num_slices=num_slices,
        evaluations=evaluations,
    )
