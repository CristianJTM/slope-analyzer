import math

from .models import SlipCircle, Slice, SlopeGeometry

_TOL = 1e-9
_X_TOL = 1e-3


def _ground_y(x: float, height: float, tan_angle: float, x_crest: float) -> float:
    if x <= 0.0:
        return 0.0
    if x < x_crest:
        return x * tan_angle
    return height


def _lower_arc_y(x: float, circle: SlipCircle) -> float:
    dx = x - circle.center_x
    return circle.center_y - math.sqrt(circle.radius**2 - dx**2)


def _intersections(geometry: SlopeGeometry, circle: SlipCircle) -> list[float]:
    """x de las intersecciones entre la superficie del terreno y el círculo."""
    cx, cy, r = circle.center_x, circle.center_y, circle.radius
    tan_angle = math.tan(math.radians(geometry.angle))
    height = geometry.height
    x_crest = height / tan_angle if tan_angle > 0 else math.inf
    xs: list[float] = []

    # Base horizontal y=0, x<=0
    disc = r * r - cy * cy
    if disc >= 0:
        root = math.sqrt(disc)
        for x in (cx - root, cx + root):
            if x <= _X_TOL:
                xs.append(x)

    # Cara del talud y=x*tan_angle, 0 < x < x_crest
    if tan_angle > 0 and math.isfinite(x_crest):
        a = -(1.0 + tan_angle * tan_angle)
        b = 2.0 * (cx + cy * tan_angle)
        c = r * r - cx * cx - cy * cy
        disc2 = b * b - 4.0 * a * c
        if disc2 >= 0:
            root2 = math.sqrt(disc2)
            for x in ((-b - root2) / (2.0 * a), (-b + root2) / (2.0 * a)):
                if _X_TOL < x < x_crest - _X_TOL and cy - tan_angle * x >= -_X_TOL:
                    xs.append(x)

    # Cresta horizontal y=height, x>=x_crest
    disc3 = r * r - (cy - height) ** 2
    if disc3 >= 0:
        root3 = math.sqrt(disc3)
        for x in (cx - root3, cx + root3):
            if x >= x_crest - _X_TOL:
                xs.append(x)

    xs.sort()
    unique: list[float] = []
    for x in xs:
        if not unique or abs(x - unique[-1]) > _X_TOL:
            unique.append(x)
    return unique


def _mass_bounds(
    geometry: SlopeGeometry,
    circle: SlipCircle,
    tan_angle: float,
    x_crest: float,
) -> tuple[float, float]:
    """Fronteras (x_left, x_right) de la masa deslizante que contiene la cara.

    Un círculo grande puede cortar el terreno en más de dos puntos (p. ej. por
    debajo de la planicie del pie). Se toma solo el tramo de masa que contiene
    la cara del talud, no el corte más a la izquierda.
    """
    cx, r = circle.center_x, circle.radius
    left_end, right_end = cx - r, cx + r
    if not math.isfinite(x_crest):
        x_crest = right_end

    def height(x: float) -> float:
        return _ground_y(x, geometry.height, tan_angle, x_crest) - _lower_arc_y(
            x, circle
        )

    crossings = _intersections(geometry, circle)
    points = set(crossings)
    points.update({0.0, x_crest, left_end, right_end})

    xs = sorted(x for x in points if left_end - _X_TOL <= x <= right_end + _X_TOL)
    unique: list[float] = []
    for x in xs:
        if not unique or abs(x - unique[-1]) > _X_TOL:
            unique.append(x)

    intervals = [
        (a, b) for a, b in zip(unique, unique[1:]) if height(0.5 * (a + b)) > 0.0
    ]

    merged: list[tuple[float, float]] = []
    for a, b in intervals:
        is_crossing = any(abs(a - x) <= _X_TOL for x in crossings)
        if (
            merged
            and abs(merged[-1][1] - a) <= _TOL
            and not is_crossing
            and height(a) > _TOL
        ):
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))

    if x_crest > _TOL:
        best: tuple[float, float] | None = None
        best_overlap = 0.0
        for a, b in merged:
            overlap = min(b, x_crest) - max(a, 0.0)
            if overlap > best_overlap:
                best_overlap, best = overlap, (a, b)
        if best is None:
            raise ValueError("el círculo no define una masa deslizante en el talud")
        return best

    for a, b in merged:
        if a <= _TOL and b > _TOL:
            return (a, b)
    raise ValueError("el círculo no define una masa deslizante en el talud")


def slice_slope(
    geometry: SlopeGeometry,
    slip_circle: SlipCircle,
    num_slices: int = 10,
) -> list[Slice]:
    """Divide la masa deslizante en `num_slices` dovelas verticales.

    El arco de falla es la porción inferior del círculo, entre sus dos
    intersecciones con la superficie del terreno.

    Lanza ValueError si height <= 0, num_slices < 1, o el círculo no define
    una masa deslizante sobre el talud.
    """
    if geometry.height <= 0:
        raise ValueError("height debe ser > 0")
    if num_slices < 1:
        raise ValueError("num_slices debe ser >= 1")
    if slip_circle.radius <= 0:
        raise ValueError("radius debe ser > 0")

    tan_angle = math.tan(math.radians(geometry.angle))
    x_crest = geometry.height / tan_angle if tan_angle > 0 else math.inf
    x_left, x_right = _mass_bounds(geometry, slip_circle, tan_angle, x_crest)
    if x_right - x_left <= _TOL:
        raise ValueError("el círculo no define una masa deslizante en el talud")

    width = (x_right - x_left) / num_slices
    slices: list[Slice] = []
    for i in range(num_slices):
        x_mid = x_left + (i + 0.5) * width
        dx = x_mid - slip_circle.center_x
        cos_a = math.sqrt(max(0.0, slip_circle.radius**2 - dx * dx)) / slip_circle.radius
        sin_a = dx / slip_circle.radius
        base_angle = math.degrees(math.atan2(sin_a, cos_a))
        h = _ground_y(
            x_mid, geometry.height, tan_angle, x_crest
        ) - _lower_arc_y(x_mid, slip_circle)
        slices.append(Slice(width=width, height=max(0.0, h), base_angle=base_angle))
    return slices
