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
