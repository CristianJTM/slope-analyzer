import pytest

from app.core.bishop import bishop_fs
from app.core.models import SlopeGeometry, SoilParams
from app.core.search import SearchBounds, critical_circle
from app.core.slicing import slice_slope

GEOMETRY = SlopeGeometry(height=10.0, angle=26.565051)
SOIL = SoilParams(cohesion=10.0, phi=20.0, gamma=20.0, ru=0.25)


def test_finds_circle_at_least_as_good_as_known():
    result = critical_circle(GEOMETRY, SOIL, "bishop")
    # El círculo conocido (FS 1.1001) no debería ser mejor que el mínimo.
    assert result.fs <= 1.1001 + 5e-3


def test_matches_reference_minimum():
    result = critical_circle(GEOMETRY, SOIL, "bishop")
    assert result.fs == pytest.approx(1.10, rel=5e-2)


def test_returned_circle_recomputes_same_fs():
    result = critical_circle(GEOMETRY, SOIL, "bishop")
    slices = slice_slope(GEOMETRY, result.slip_circle, num_slices=result.num_slices)
    assert bishop_fs(slices, SOIL).fs == pytest.approx(result.fs, rel=1e-9)


def test_fellenius_lower_than_bishop():
    bishop = critical_circle(GEOMETRY, SOIL, "bishop")
    fellenius = critical_circle(GEOMETRY, SOIL, "fellenius")
    assert fellenius.fs < bishop.fs


def test_invalid_bounds_raise():
    # x_min >= x_max: bounds degenerados.
    bounds = SearchBounds(x_min=10.0, x_max=10.0, y_min=0.0, y_max=10.0)
    with pytest.raises(ValueError):
        critical_circle(GEOMETRY, SOIL, "bishop", bounds=bounds, grid=3)


def test_unknown_method_raises():
    with pytest.raises(ValueError):
        critical_circle(GEOMETRY, SOIL, "janbu")


def test_deep_circle_supported():
    # Con bounds profundos, la búsqueda explora círculos con centro muy alto
    # (falla profunda). El FS del círculo exacto ya se valida en test_slicing.
    bounds = SearchBounds(x_min=-16.5, x_max=-14.5, y_min=67.5, y_max=69.5)
    soil = SoilParams(cohesion=0.0, phi=30.0, gamma=20.0, ru=0.0)
    result = critical_circle(
        GEOMETRY, soil, "bishop", bounds=bounds, grid=7, depths=(1.746,)
    )
    assert result.slip_circle.center_y > 60.0
    assert 0.0 < result.fs < 2.0
