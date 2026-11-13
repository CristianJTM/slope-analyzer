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


# Caso de referencia (Bishop simplificado, seco) contra software de estabilidad.
# Centro (34.206, 47.4018), R=22.7932, FS=1.37563.
# Se traslada el pie (30, 25) a (0, 0) y se le resta (30, 25) al centro.
REF_HEIGHT = 10.0        # m
REF_ANGLE = 26.565051    # grados (atan(10/20))
REF_COHESION = 10.0      # kPa
REF_PHI = 20.0           # grados
REF_GAMMA = 20.0         # kN/m³
REF_RU = 0.0             # adimensional (seco)
REF_CIRCLE = SlipCircle(center_x=4.206, center_y=22.4018, radius=22.7932)  # m
REF_EXPECTED_FS = 1.37563
REF_NUM_SLICES = 50


def test_reference_benchmark():
    # T3: end-to-end (slice_slope + bishop_fs) contra software de referencia.
    geometry = SlopeGeometry(height=REF_HEIGHT, angle=REF_ANGLE)
    soil = SoilParams(
        cohesion=REF_COHESION,
        phi=REF_PHI,
        gamma=REF_GAMMA,
        ru=REF_RU,
    )
    slices = slice_slope(geometry, REF_CIRCLE, num_slices=REF_NUM_SLICES)
    result = bishop_fs(slices, soil)
    assert result.fs == pytest.approx(REF_EXPECTED_FS, rel=2e-2)  # ±2%


def test_reference_benchmark_ru():
    # Mismo caso con ru=0.25. FS de referencia = 1.101, mismo círculo.
    geometry = SlopeGeometry(height=REF_HEIGHT, angle=REF_ANGLE)
    soil = SoilParams(
        cohesion=REF_COHESION,
        phi=REF_PHI,
        gamma=REF_GAMMA,
        ru=0.25,
    )
    slices = slice_slope(geometry, REF_CIRCLE, num_slices=REF_NUM_SLICES)
    result = bishop_fs(slices, soil)
    assert result.fs == pytest.approx(1.101, rel=2e-2)  # ±2%


# Caso c=0 (seco). El círculo es muy grande y su centro queda a la izquierda
# del pie; la masa válida empieza en el toe, no en el corte lejano.
# Centro (14.4321, 93.5343), R=70.2803, FS=1.30087 (trasladado -30, -25).
REF_C0_HEIGHT = 10.0
REF_C0_ANGLE = 26.565051
REF_C0_COHESION = 0.0
REF_C0_PHI = 30.0
REF_C0_GAMMA = 20.0
REF_C0_CIRCLE = SlipCircle(center_x=-15.5679, center_y=68.5343, radius=70.2803)
REF_C0_EXPECTED_FS = 1.30087
REF_C0_NUM_SLICES = 50


def test_reference_benchmark_c0():
    geometry = SlopeGeometry(height=REF_C0_HEIGHT, angle=REF_C0_ANGLE)
    soil = SoilParams(
        cohesion=REF_C0_COHESION,
        phi=REF_C0_PHI,
        gamma=REF_C0_GAMMA,
    )
    slices = slice_slope(geometry, REF_C0_CIRCLE, num_slices=REF_C0_NUM_SLICES)
    # La masa debe arrancar en el toe (x=0) y terminar en la cresta (x~23.33).
    assert sum(s.width for s in slices) == pytest.approx(23.33, abs=0.05)
    result = bishop_fs(slices, soil)
    assert result.fs == pytest.approx(REF_C0_EXPECTED_FS, rel=2e-2)  # ±2%
