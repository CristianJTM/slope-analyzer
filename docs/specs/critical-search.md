# Búsqueda del círculo crítico — Especificación

Encontrar el círculo de falla con FS mínimo (Bishop o Fellenius) en lugar de
requerir un círculo fijo.

## Algoritmo (`core/search.py`)

```python
critical_circle(
    geometry, soil, method="bishop",
    *, bounds=None, grid=15, depths=(0.0,), num_slices=50,
) -> CriticalCircle
```

- **Bounds por defecto**: `x ∈ [−0.5·L, 1.5·L]`, `y ∈ [H, 3H]`, con
  `L = H/tan(angle)` (o `H` si el talud es vertical).
- **Grid de centros** `(xc, yc)`; por cada centro se evalúan:
  - **círculo por el pie**: radio = distancia del centro al pie `(0,0)`;
  - **círculos profundos**: tangentes a `y = −d` para cada `d ∈ depths`
    (radio = `yc + d`).
- Los candidatos inválidos (`slice_slope` lanza `ValueError`) se descartan.
- **Grid grueso + refinamiento local** alrededor del mejor centro.
- Devuelve `CriticalCircle(fs, slip_circle, method, num_slices, evaluations)`.
- Si no hay ningún círculo válido en la región → `ValueError`.

## API

`POST /api/v1/search`

```jsonc
{
  "method": "bishop",
  "geometry": { "height": 10.0, "angle": 26.565 },
  "soil": { "cohesion": 10.0, "phi": 20.0, "gamma": 20.0, "ru": 0.25 },
  "num_slices": 50,
  "grid": 15,
  "depths": [0.0]
}
```

Respuesta:

```jsonc
{
  "fs": 1.0988,
  "slip_circle": { "center_x": 4.286, "center_y": 21.429, "radius": 21.853 },
  "method": "bishop",
  "num_slices": 50,
  "evaluations": 851
}
```

`bounds` es opcional; `depths` por defecto `[0.0]`. No persiste en el historial
(eso queda para `/analyze`).

## Tests (`tests/test_search.py`)

- El mínimo encontrado ≤ FS del círculo conocido.
- FS ≈ mínimo de referencia (±5 %).
- El círculo devuelto recalcula el mismo FS.
- Fellenius < Bishop sobre la misma búsqueda.
- Bounds degenerados → `ValueError`.
- Método desconocido → `ValueError`.
- Con bounds profundos se exploran círculos de centro alto (falla profunda).

## Fuera de alcance

- Estratigrafía y nivel freático.
- Optimización continua; se usa grid + refinamiento.
