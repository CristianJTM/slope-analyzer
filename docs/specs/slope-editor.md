# Editor geométrico CAD — Especificación

Editor de la geometría del talud como polígono cerrado, estilo CAD, en el
frontend. Etapa 1: dibujo y validación (todavía no conectado al cálculo).

## Coordenadas

- Metros, `x` a la derecha, `y` hacia arriba.
- Mapeo fijo mundo→pantalla (escala px/m + origen) con grilla visible.

## Interacciones

- **Hover**: línea elástica desde el último vértice al cursor, con largo (m) y
  ángulo (°) en vivo.
- **Click** en el fondo: agrega un vértice.
- **Drag** sobre un vértice: lo mueve.
- **Comando** (input + toggle de modo):
  - `polar` (`ángulo-largo`): `90-5` → vertical 5 m hacia arriba.
  - `coord` (`x-y`): `2-5` → coordenada absoluta `(2,5)`.
- **Deshacer** (borra el último) y **Limpiar**.
- Ángulo en grados, antihorario desde `+x` (90° = arriba).

## Snapping

- **Grilla**: redondea a `GRID_SIZE = 1 m` (toggle).
- **Object snap de vértice**: si el punto está a ≤ `OSNAP_TOL = 0.5 m` de un
  vértice existente, se imanta a él (toggle + marcador cuadrado verde).
- Prioridad: object snap de vértice > snap de grilla.
- Los comandos escritos son exactos (no se imantan).

## Validación

- La figura siempre se cierra (el polígono une el último vértice con el
  primero).
- **Válido** con ≥ `MIN_VERTICES = 6` (6 aristas incluyendo el cierre).

## Estructura

```
frontend/src/
  components/SlopeEditor.tsx   # SVG, grilla, interacciones, panel de info
  hooks/useSlopeEditor.ts      # vertices[], modo, snaps, comandos, validación
```

## Fuera de alcance (etapa 1)

- Conectar el polígono al cálculo (requiere geometría libre en `core`).
- Exportar/importar JSON, pan/zoom, más tipos de object snap (punto medio,
  perpendicular), capas y estratigrafía.
