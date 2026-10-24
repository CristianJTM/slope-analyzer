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
