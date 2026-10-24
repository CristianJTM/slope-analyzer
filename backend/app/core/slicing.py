import math

from .models import SlipCircle, Slice, SlopeGeometry


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
            if x <= 1e-9:
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
                if 1e-9 < x < x_crest - 1e-9 and cy - tan_angle * x >= -1e-9:
                    xs.append(x)

    # Cresta horizontal y=height, x>=x_crest
    disc3 = r * r - (cy - height) ** 2
    if disc3 >= 0:
        root3 = math.sqrt(disc3)
        for x in (cx - root3, cx + root3):
            if x >= x_crest - 1e-9:
                xs.append(x)

    xs.sort()
    unique: list[float] = []
    for x in xs:
        if not unique or abs(x - unique[-1]) > 1e-6:
            unique.append(x)
    return unique


def slice_slope(
    geometry: SlopeGeometry,
    slip_circle: SlipCircle,
    num_slices: int = 10,
) -> list[Slice]:
    """Divide la masa deslizante en `num_slices` dovelas verticales.

    El arco de falla es la porción inferior del círculo, entre sus dos
    intersecciones con la superficie del terreno.

    Lanza ValueError si height <= 0, num_slices < 1, o el círculo no corta
    el terreno en dos puntos.
    """
    if geometry.height <= 0:
        raise ValueError("height debe ser > 0")
    if num_slices < 1:
        raise ValueError("num_slices debe ser >= 1")
    if slip_circle.radius <= 0:
        raise ValueError("radius debe ser > 0")

    xs = _intersections(geometry, slip_circle)
    if len(xs) < 2:
        raise ValueError("el círculo no corta el terreno en dos puntos")
    x_left, x_right = xs[0], xs[-1]
    if x_right - x_left <= 1e-9:
        raise ValueError("el círculo no corta el terreno en dos puntos")

    tan_angle = math.tan(math.radians(geometry.angle))
    x_crest = geometry.height / tan_angle if tan_angle > 0 else math.inf
    width = (x_right - x_left) / num_slices

    slices: list[Slice] = []
    for i in range(num_slices):
        x_mid = x_left + (i + 0.5) * width
        dx = x_mid - slip_circle.center_x
        cos_a = math.sqrt(max(0.0, slip_circle.radius**2 - dx * dx)) / slip_circle.radius
        sin_a = dx / slip_circle.radius
        base_angle = math.degrees(math.atan2(sin_a, cos_a))
        h = _ground_y(x_mid, geometry.height, tan_angle, x_crest) - _lower_arc_y(
            x_mid, slip_circle
        )
        slices.append(Slice(width=width, height=max(0.0, h), base_angle=base_angle))
    return slices
