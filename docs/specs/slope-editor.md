# Editor geométrico CAD — Especificación

Editor de la geometría del talud como polígono cerrado, estilo CAD, en el
frontend. Etapa 1: dibujo y validación (todavía no conectado al cálculo).

## Coordenadas

- Metros, `x` a la derecha, `y` hacia arriba.
- Mapeo fijo mundo→pantalla (escala px/m + origen) con grilla visible.

## Cursor y snap

- El cursor es **libre**: no salta a la grilla al moverse.
- Al pasar cerca de un vértice (≤ `OSNAP_TOL = 0.5 m`) se muestra un
  **marcador verde** de sugerencia (sin mover el cursor).
- El **snap se aplica recién al hacer click**: primero vértice, luego grilla
  (si el toggle está activo), si no, posición libre.
- Al arrastrar, el vértice se mueve libre.

## Interacciones

- **Hover**: línea elástica desde el último vértice al cursor libre, con largo
  (m) y ángulo (°) en vivo.
- **Click** en el fondo: agrega un vértice (con snap).
- **Drag** sobre un vértice: lo mueve.
- **Comando** (input fijo + modo Polar / Coordenada):
  - `polar` (`ángulo-largo`): `90-5` → vertical 5 m hacia arriba.
  - `coord` (`x-y`): `2-5` → coordenada absoluta `(2,5)`.
- **Teclado** (con el puntero sobre el canvas y foco fuera de inputs):
  - dígitos / `.` / `-` arman el comando;
  - `Enter` agrega; `Esc` borra; `Backspace` borra el último carácter;
  - `P` / `C` cambian a modo Polar / Coordenada.
- **Deshacer** (borra el último) y **Limpiar**.
- Ángulo en grados, antihorario desde `+x` (90° = arriba).

## Entrada dinámica

- Panel flotante **junto al cursor** (solo lectura, `pointer-events: none`):
  coordenadas, `L` y `θ` en vivo, modo actual y comando en curso.

## Validación

- La figura siempre se cierra (el polígono une el último vértice con el
  primero).
- **Válido** con ≥ `MIN_VERTICES = 6` (6 aristas incluyendo el cierre).

## Estructura

```
frontend/src/
  components/SlopeEditor.tsx   # SVG, grilla, interacciones, panel flotante
  hooks/useSlopeEditor.ts      # vertices[], modo, snaps, comandos, validación
```

## Fuera de alcance (etapa 1)

- Conectar el polígono al cálculo (requiere geometría libre en `core`).
- Exportar/importar JSON, pan/zoom, más tipos de object snap (punto medio,
  perpendicular), capas y estratigrafía.
