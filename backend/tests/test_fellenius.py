import pytest

from app.core.bishop import bishop_fs
from app.core.fellenius import fellenius_fs
from app.core.models import Slice, SoilParams


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
    # c=10, φ=20°, ru=0.25. FS calculado a mano ≈ 1.0752.
    soil = SoilParams(cohesion=10.0, phi=20.0, gamma=20.0, ru=0.25)
    fs = fellenius_fs(_three_asymmetric_slices(), soil)
    assert fs == pytest.approx(1.0752, abs=3e-3)


def test_fellenius_lower_than_bishop():
    # El método ordinario no incluye fuerzas entre dovelas: FS menor que Bishop.
    soil = SoilParams(cohesion=10.0, phi=20.0, gamma=20.0, ru=0.25)
    slices = _three_asymmetric_slices()
    assert fellenius_fs(slices, soil) < bishop_fs(slices, soil).fs


def test_empty_slices_raises():
    with pytest.raises(ValueError):
        fellenius_fs([], SoilParams(cohesion=10.0, phi=30.0, gamma=20.0))
