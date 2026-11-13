# slope-analyzer

Analizador de estabilidad de taludes (métodos **Bishop Simplificado** y
**Fellenius**). Proyecto personal de portafolio que combina ingeniería
geotécnica con desarrollo de software.

> ⚠️ En desarrollo. No usar para diseño real sin validar contra un software de
> estabilidad de taludes de referencia.

## Estado actual

**Fase 1 — Bishop Simplificado (completa y validada contra software de
referencia)**

- Módulo de cálculo en Python puro (sin servidor).
- Dovelas (`slice`) generadas desde la geometría del talud + círculo de falla
  (`slip_circle`), o ingresadas directamente.
- Presión de poros modelada con `ru`.
- Validado contra software de referencia (Bishop simplificado): seco
  (`FS 1.3747` vs `1.37563`), con `ru = 0.25` (`1.1001` vs `1.101`) y con
  `c = 0` (`1.3009` vs `1.30087`).

**Fase 2 — Fellenius (en curso)**

- Núcleo del método ordinario implementado + tests.
- ⏳ Validación externa pendiente.

12 tests en verde.

## Stack

- Backend: Python 3.11+ (probado con 3.12)
- Tests: `pytest`
- Futuro: FastAPI + SQLite + React/Vite/TypeScript + Docker Compose

## Estructura

```
backend/
  app/core/        # lógica de cálculo pura (sin FastAPI)
    models.py      # dataclasses del dominio
    slicing.py     # slice_slope(): geometría -> dovelas
    bishop.py      # bishop_fs(): dovelas -> factor de seguridad
    fellenius.py   # fellenius_fs(): método ordinario (sin iterar)
  tests/           # pruebas con pytest
docs/specs/        # especificaciones de cada módulo
```

## Glosario (dominio)

| Término | Significado |
|---|---|
| `fs` | factor de seguridad |
| `slice` | dovela |
| `slip_circle` | círculo de falla |
| `cohesion` | cohesión (kPa) |
| `phi` | ángulo de fricción interna (grados) |
| `gamma` | peso unitario (kN/m³) |

## Cómo correr los tests

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements-dev.txt

cd backend
python -m pytest
```

## Método

Bishop Simplificado (1955), método de las dovelas:

```
FS = Σ [ (cohesion·b + W·(1 − ru)·tan φ) / m_α ] / Σ [ W·sin α ]
m_α = cos α · (1 + tan α · tan φ / FS)
```

Iteración desde `FS = 1.0` hasta convergencia.

Fellenius (método ordinario), sin iteración:

```
FS = Σ [ cohesion·Δl + (W·cos α − ru·W/cos α)·tan φ ] / Σ [ W·sin α ]
Δl = b / cos α
```

## Hoja de ruta

1. ~~Fase 1 — Bishop Simplificado~~: núcleo + tests (completa).
2. ~~Validación contra software de referencia (seco y `ru`)~~ (completa).
3. **Fase 2 — Fellenius** (en curso): núcleo + tests; falta validación externa.
4. **Fase 3** — API FastAPI + persistencia SQLite.
5. **Fase 4** — Frontend React/Vite/TypeScript.
6. **Fase 5** — Docker Compose + CI con GitHub Actions.

Este README se actualiza al cerrar cada fase.
