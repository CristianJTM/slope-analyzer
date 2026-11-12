# slope-analyzer — Contexto para agentes IA

## Qué es esto
Analizador de estabilidad de taludes (métodos Bishop Simplificado y Fellenius).
Proyecto personal de portafolio — prioriza código legible y bien testeado sobre
velocidad de entrega.

## Autor
Ingeniero Civil (muros de contención, proyectos viales) en transición a desarrollo.
Estudiante de Analista Programador (penúltimo bimestre). Conoce bien el dominio
geotécnico; está aprendiendo patrones de arquitectura de software.

## Stack
- Backend: Python 3.11 + FastAPI
- Frontend: React + Vite + TypeScript
- DB: SQLite (volumen Docker)
- Infra: Docker Compose, todo local (sin AWS/Azure)
- CI/CD: GitHub Actions

## Convenciones de nombres (glosario del dominio)
- `fs` = factor de seguridad (NUNCA `safety_factor` o `sf`)
- `slice` = dovela (en cálculos de rebanadas del talud)
- `slip_circle` = círculo de falla
- `cohesion` = cohesión del suelo (kPa)
- `phi` = ángulo de fricción interna (grados)
- `gamma` = peso unitario del suelo (kN/m³)

## Estructura
backend/app/core/     → lógica de cálculo pura, sin dependencias de FastAPI
backend/app/api/      → rutas, solo orquestan llamadas a core/
backend/app/models/   → esquemas Pydantic
frontend/src/components/ → componentes React
frontend/src/api/     → cliente HTTP tipado

## Reglas de trabajo
- Los módulos de cálculo (core/) deben ser 100% testeables sin levantar el servidor
- Toda función de cálculo geotécnico necesita al menos un test con valores de
  referencia conocidos (comparar contra Slide2 u otro software si es posible)
- No mencionar por nombre el software de validación externo en commits, README
  ni código; usar "software de referencia"
- No agregar dependencias nuevas sin justificar por qué la estándar no alcanza
- Responde de forma concisa: código exacto, explicaciones breves, sin relleno

## Lo que NO hacer
- No usar librerías de UI pesadas (Material UI, Ant Design) — Tailwind + componentes propios
- No optimizar prematuramente — primero que funcione y esté testeado
- No mezclar lógica de cálculo con lógica de presentación