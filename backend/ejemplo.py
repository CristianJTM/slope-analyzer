"""Prueba manual del núcleo Bishop Simplificado.

Correr desde backend/:

    cd backend
    python ejemplo.py

Editá los datos de entrada de abajo para probar otros casos (p. ej. una
geometría y un círculo de un software de referencia).
"""

from app.core.bishop import bishop_fs
from app.core.models import SlipCircle, SlopeGeometry, SoilParams
from app.core.slicing import slice_slope

# --- Datos de entrada (caso de referencia) ---
geometry = SlopeGeometry(height=10.0, angle=26.565051)              # m, grados
slip_circle = SlipCircle(center_x=4.206, center_y=22.4018, radius=22.7932)  # m
soil = SoilParams(cohesion=10.0, phi=20.0, gamma=20.0, ru=0.25)    # kPa, grados, kN/m³
num_slices = 50


def main() -> None:
    slices = slice_slope(geometry, slip_circle, num_slices=num_slices)
    result = bishop_fs(slices, soil)

    print(f"Talud:  H={geometry.height} m, angulo={geometry.angle} deg")
    print(
        f"Circulo: centro=({slip_circle.center_x}, {slip_circle.center_y}) m, "
        f"R={slip_circle.radius} m"
    )
    print(
        f"Suelo:  cohesion={soil.cohesion} kPa, phi={soil.phi} deg, "
        f"gamma={soil.gamma} kN/m3, ru={soil.ru}"
    )
    print(f"Dovelas: {len(slices)}")
    print()
    print(f"{'#':>2}  {'b (m)':>8}  {'h (m)':>8}  {'alpha (deg)':>11}")
    for i, s in enumerate(slices, start=1):
        print(f"{i:>2}  {s.width:>8.2f}  {s.height:>8.2f}  {s.base_angle:>11.2f}")
    print()
    print(
        f"FS = {result.fs:.4f}  "
        f"(iteraciones={result.iterations}, convergido={result.converged})"
    )


if __name__ == "__main__":
    main()
