# Frontend — Especificación (Fase 4)

MVP de interfaz para el análisis de estabilidad: formulario → API → resultado
e historial. Una sola página, sin router ni librerías de UI.

## Stack

- React + Vite + TypeScript
- Tailwind (componentes propios)

## Backend

Requiere CORS para `http://localhost:5173` y `http://127.0.0.1:5173`
(configurado en `app/main.py`). Endpoints usados: `POST /api/v1/analyze`,
`GET /api/v1/analyses`.

## Estructura

```
frontend/
  index.html
  package.json
  tsconfig.json
  vite.config.ts
  src/
    main.tsx
    App.tsx
    styles.css
    api/types.ts        # interfaces TS (espejo de schemas.py)
    api/client.ts       # fetch + manejo de errores
    api/analysis.ts     # analyze() y listAnalyses()
    hooks/useAnalyses.ts
    components/SlopeForm.tsx
    components/ResultPanel.tsx
    components/HistoryList.tsx
```

## Flujo

1. Al montar, `useAnalyses` carga el historial (`GET /analyses`).
2. `SlopeForm` arma el `AnalyzeRequest` y llama a `analyze()`.
3. `ResultPanel` muestra `fs`, iteraciones y convergencia.
4. `HistoryList` se refresca tras cada cálculo.

## Tipos

Los tipos TS espejan los esquemas Pydantic (`AnalyzeRequest`,
`AnalysisRecord`, `AnalysisResult`), manteniendo `cohesion`, `phi`, `gamma`,
`ru`, `slip_circle`, `fs`.

## Correr

```powershell
cd frontend
npm install
npm run dev        # http://localhost:5173
npm run build      # type-check + build
```

## Fuera de alcance

- Visualización SVG del talud/círculo.
- Router y autenticación.
- Tests de UI (Vitest + Testing Library).
