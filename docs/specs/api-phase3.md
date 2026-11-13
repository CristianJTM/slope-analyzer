# API Core — Especificación (Fase 3)

Exponer el núcleo de cálculo (Bishop y Fellenius) por HTTP con FastAPI y
persistir un historial de corridas en SQLite.

## Endpoints

### `POST /api/v1/analyze`

Ejecuta un análisis y guarda la corrida.

```jsonc
{
  "method": "bishop",               // "bishop" | "fellenius"
  "geometry": { "height": 10.0, "angle": 26.565 },
  "slip_circle": { "center_x": 4.206, "center_y": 22.4018, "radius": 22.7932 },
  "soil": { "cohesion": 10.0, "phi": 20.0, "gamma": 20.0, "ru": 0.25 },
  "num_slices": 50
}
```

Respuesta `201`:

```jsonc
{
  "id": 1,
  "method": "bishop",
  "created_at": "2026-11-12T...",
  "input": { ... },
  "result": { "fs": 1.1001, "iterations": 5, "converged": true }
}
```

Para `fellenius`, `result.iterations` y `result.converged` son `null`.

Payload inválido → `422`.

### `GET /api/v1/analyses`

Devuelve la lista de corridas guardadas (orden por `id`).

## Arquitectura por capas

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| Dominio | `core/` | cálculo puro, sin FastAPI ni DB |
| DTOs | `models/` | esquemas Pydantic de request/response |
| Aplicación | `services/` | mapea DTO→dominio, orquesta core, persiste |
| Presentación | `api/` | endpoints, solo delegan |
| Persistencia | `db/` | engine, tabla y repository SQLite |

Los dataclasses de `core/` son el dominio; los `...In` de `models/` son los
DTOs. El cálculo no se mezcla con HTTP ni con la base de datos.

## Estructura

```
backend/
  app/
    main.py
    core/                  # (ya existe)
    models/schemas.py
    services/analysis.py
    api/routes.py
    db/database.py
    db/models.py
    db/repository.py
  tests/test_api.py
```

## Persistencia

Tabla `analyses` con: `id`, `method`, `created_at`, `input` (JSON),
`result` (JSON). Se crea con `Base.metadata.create_all` al arrancar.

## Dependencias

- Runtime: `fastapi`, `uvicorn`, `sqlalchemy`.
- Dev (tests): `pytest`, `httpx` (requerido por `TestClient`).

## Tests

Con `TestClient` y SQLite en memoria (override de `get_db`):

- `POST /analyze` bishop → `201`, `fs ≈ 1.1001`.
- `POST /analyze` fellenius → `201`, `fs ≈ 1.0768`, `iterations = null`.
- `method` inválido → `422`.
- input inválido (`gamma = 0`) → `422`.
- `GET /analyses` devuelve las corridas guardadas en orden.

## Fuera de alcance

Auth, búsqueda del círculo crítico, estratigrafía/nivel freático,
migraciones Alembic (se usa `create_all`) y dockerización.
