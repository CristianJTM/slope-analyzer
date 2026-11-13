import pytest

from app.core.bishop import bishop_fs
from app.core.fellenius import fellenius_fs
from app.core.models import SlipCircle, Slice, SlopeGeometry, SoilParams
from app.core.slicing import slice_slope


def _two_slices() -> list[Slice]:
    return [
        Slice(width=2.0, height=3.0, base_angle=20.0),
        Slice(width=2.0, height=3.0, base_angle=20.0),
    ]


def _three_asymmetric_slices() -> list[Slice]:
    return [
        Slice(width=2.0, height=5.0, base_angle=10.0),
        Slice(width=2.0, height=4.0, base_angle=25.0),
        Slice(width=2.0, height=2.0, base_angle=45.0),
    ]


def test_friction_only_hand_verified():
    # c=0, ru=0. FS = tan φ / tan α ≈ 1.5863 (calculado a mano).
    soil = SoilParams(cohesion=0.0, phi=30.0, gamma=20.0, ru=0.0)
    fs = fellenius_fs(_two_slices(), soil)
    assert fs == pytest.approx(1.5863, abs=1e-3)


def test_three_slices_hand_verified():
    # c=10, φ=20°, ru=0.25. Peso efectivo W(1-ru): FS ≈ 1.1292 (a mano).
    soil = SoilParams(cohesion=10.0, phi=20.0, gamma=20.0, ru=0.25)
    fs = fellenius_fs(_three_asymmetric_slices(), soil)
    assert fs == pytest.approx(1.1292, abs=3e-3)


# Benchmark contra software de referencia (Ordinary/Fellenius, seco con ru).
REF_HEIGHT = 10.0
REF_ANGLE = 26.565051
REF_COHESION = 10.0
REF_PHI = 20.0
REF_GAMMA = 20.0
REF_RU = 0.25
REF_CIRCLE = SlipCircle(center_x=5.9399, center_y=18.3567, radius=19.2938)
REF_EXPECTED_FS = 1.07797
REF_NUM_SLICES = 50


def test_reference_benchmark():
    geometry = SlopeGeometry(height=REF_HEIGHT, angle=REF_ANGLE)
    soil = SoilParams(
        cohesion=REF_COHESION,
        phi=REF_PHI,
        gamma=REF_GAMMA,
        ru=REF_RU,
    )
    slices = slice_slope(geometry, REF_CIRCLE, num_slices=REF_NUM_SLICES)
    fs = fellenius_fs(slices, soil)
    assert fs == pytest.approx(REF_EXPECTED_FS, rel=2e-2)  # ±2%


def test_fellenius_lower_than_bishop():
    # En un círculo real, el método ordinario da FS menor que Bishop.
    geometry = SlopeGeometry(height=REF_HEIGHT, angle=REF_ANGLE)
    soil = SoilParams(
        cohesion=REF_COHESION,
        phi=REF_PHI,
        gamma=REF_GAMMA,
        ru=REF_RU,
    )
    slices = slice_slope(geometry, REF_CIRCLE, num_slices=REF_NUM_SLICES)
    assert fellenius_fs(slices, soil) < bishop_fs(slices, soil).fs


def test_empty_slices_raises():
    with pytest.raises(ValueError):
        fellenius_fs([], SoilParams(cohesion=10.0, phi=30.0, gamma=20.0))
