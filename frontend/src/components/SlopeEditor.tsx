import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type MouseEvent,
  type PointerEvent,
} from "react";
import {
  GRID_SIZE,
  MIN_VERTICES,
  OSNAP_TOL,
  nearestVertex,
  resolvePoint,
  useSlopeEditor,
  type Point,
} from "../hooks/useSlopeEditor";

const VIEW_W = 860;
const VIEW_H = 560;
const PPM = 40; // píxeles por metro
const ORIGIN_X = 60;
const ORIGIN_Y = VIEW_H - 60;

function worldToScreen(p: Point): Point {
  return { x: ORIGIN_X + p.x * PPM, y: ORIGIN_Y - p.y * PPM };
}

function screenToWorld(p: Point): Point {
  return { x: (p.x - ORIGIN_X) / PPM, y: (ORIGIN_Y - p.y) / PPM };
}

function fmt(value: number): string {
  return value.toFixed(2);
}

export default function SlopeEditor() {
  const {
    vertices,
    mode,
    setMode,
    snapGrid,
    setSnapGrid,
    snapVertex,
    setSnapVertex,
    editing,
    setEditing,
    message,
    commandBuffer,
    addVertex,
    moveVertex,
    undo,
    clear,
    applyCommand,
    appendCommandChar,
    backspaceCommand,
    clearCommand,
    submitCommand,
  } = useSlopeEditor();

  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoverFree, setHoverFree] = useState<Point | null>(null);
  const [snapSuggestion, setSnapSuggestion] = useState<Point | null>(null);
  const [dragging, setDragging] = useState<number | null>(null);
  const [hovering, setHovering] = useState(false);
  const [pointer, setPointer] = useState({ left: 0, top: 0 });
  const [command, setCommand] = useState("");

  function eventToWorld(
    e: PointerEvent<SVGSVGElement> | MouseEvent<SVGRectElement>,
  ): Point | null {
    const svg = svgRef.current;
    const ctm = svg?.getScreenCTM();
    if (!svg || !ctm) return null;
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgPoint = pt.matrixTransform(ctm.inverse());
    return screenToWorld({ x: svgPoint.x, y: svgPoint.y });
  }

  function updatePointer(e: PointerEvent<SVGSVGElement>) {
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    const panelW = 200;
    const panelH = 92;
    const left = Math.min(e.clientX - rect.left + 16, rect.width - panelW);
    const top = Math.min(e.clientY - rect.top + 16, rect.height - panelH);
    setPointer({ left: Math.max(0, left), top: Math.max(0, top) });
  }

  function exitEditing() {
    setEditing(false);
    clearCommand();
    setHoverFree(null);
    setSnapSuggestion(null);
    setDragging(null);
  }

  function handleMove(e: PointerEvent<SVGSVGElement>) {
    if (!editing) {
      setHoverFree(null);
      setSnapSuggestion(null);
      return;
    }
    const world = eventToWorld(e);
    if (!world) return;
    setHoverFree(world);
    setSnapSuggestion(nearestVertex(world, vertices, dragging ?? undefined));
    if (dragging !== null) {
      moveVertex(dragging, world);
    }
    updatePointer(e);
  }

  function handleEnter() {
    setHovering(true);
  }

  function handleLeave() {
    setHovering(false);
    setHoverFree(null);
    setSnapSuggestion(null);
    setDragging(null);
  }

  function handleBackgroundClick(e: MouseEvent<SVGRectElement>) {
    if (!editing) {
      setEditing(true);
      return;
    }
    const world = eventToWorld(e);
    if (!world) return;
    const placed = resolvePoint(world, vertices, { snapGrid, snapVertex });
    addVertex(placed.point);
  }

  function handleVertexDown(index: number, e: PointerEvent<SVGCircleElement>) {
    e.stopPropagation();
    if (!editing) {
      setEditing(true);
      return;
    }
    setDragging(index);
  }

  function handleCommandSubmit(e: FormEvent) {
    e.preventDefault();
    applyCommand(command);
    setCommand("");
  }

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (!hovering || !editing) return;
      const el = document.activeElement;
      if (
        el instanceof HTMLInputElement ||
        el instanceof HTMLTextAreaElement ||
        el instanceof HTMLSelectElement
      ) {
        return;
      }
      if (e.key === "Enter") {
        e.preventDefault();
        submitCommand();
      } else if (e.key === "Escape") {
        e.preventDefault();
        if (commandBuffer) {
          clearCommand();
        } else {
          exitEditing();
        }
      } else if (e.key === "Backspace") {
        e.preventDefault();
        backspaceCommand();
      } else if (e.key === "p" || e.key === "P") {
        e.preventDefault();
        setMode("polar");
      } else if (e.key === "c" || e.key === "C") {
        e.preventDefault();
        setMode("coord");
      } else if (e.key.length === 1 && /[0-9.\-]/.test(e.key)) {
        e.preventDefault();
        appendCommandChar(e.key);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [
    hovering,
    editing,
    commandBuffer,
    submitCommand,
    clearCommand,
    backspaceCommand,
    appendCommandChar,
    setMode,
  ]);

  const valid = vertices.length >= MIN_VERTICES;
  const last = vertices.length > 0 ? vertices[vertices.length - 1] : null;
  const lastScreen = last ? worldToScreen(last) : null;
  const hoverScreen = hoverFree ? worldToScreen(hoverFree) : null;
  const snapScreen = snapSuggestion ? worldToScreen(snapSuggestion) : null;

  let liveLength = 0;
  let liveAngle = 0;
  if (hoverFree && last) {
    const dx = hoverFree.x - last.x;
    const dy = hoverFree.y - last.y;
    liveLength = Math.hypot(dx, dy);
    liveAngle = (Math.atan2(dy, dx) * 180) / Math.PI;
  }

  const minWorldX = Math.ceil(screenToWorld({ x: 0, y: 0 }).x);
  const maxWorldX = Math.floor(screenToWorld({ x: VIEW_W, y: 0 }).x);
  const minWorldY = Math.ceil(screenToWorld({ x: 0, y: VIEW_H }).y);
  const maxWorldY = Math.floor(screenToWorld({ x: 0, y: 0 }).y);

  const gridX: number[] = [];
  for (let x = minWorldX; x <= maxWorldX; x += GRID_SIZE) gridX.push(x);
  const gridY: number[] = [];
  for (let y = minWorldY; y <= maxWorldY; y += GRID_SIZE) gridY.push(y);

  const polygonPoints = vertices
    .map((v) => {
      const s = worldToScreen(v);
      return `${s.x},${s.y}`;
    })
    .join(" ");

  const editingControlsClass = editing ? "" : " opacity-50";

  return (
    <section className="rounded border border-slate-200 p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold">Editor de talud (CAD)</h2>
        <div className="flex items-center gap-2">
          <span
            className={`rounded px-2 py-1 text-xs font-medium ${
              valid
                ? "bg-emerald-100 text-emerald-800"
                : "bg-amber-100 text-amber-800"
            }`}
          >
            {vertices.length} vértices / {vertices.length} aristas
            {valid ? " · válido" : ` · faltan ${MIN_VERTICES - vertices.length}`}
          </span>
          {editing ? (
            <button
              type="button"
              onClick={exitEditing}
              className="rounded border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700"
            >
              Salir de edición
            </button>
          ) : (
            <>
              <span className="rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                Modo lectura
              </span>
              <button
                type="button"
                onClick={() => setEditing(true)}
                className="rounded bg-slate-900 px-3 py-1 text-xs font-medium text-white"
              >
                Editar
              </button>
            </>
          )}
        </div>
      </div>

      <div ref={containerRef} className="relative">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
          className="w-full touch-none rounded bg-white"
          style={{ aspectRatio: `${VIEW_W} / ${VIEW_H}` }}
          onPointerMove={handleMove}
          onPointerEnter={handleEnter}
          onPointerUp={() => setDragging(null)}
          onPointerLeave={handleLeave}
        >
          <rect
            x={0}
            y={0}
            width={VIEW_W}
            height={VIEW_H}
            fill="white"
            onClick={handleBackgroundClick}
          />

          {gridX.map((x) => {
            const sx = worldToScreen({ x, y: 0 }).x;
            const major = x % 5 === 0;
            return (
              <line
                key={`gx-${x}`}
                x1={sx}
                y1={0}
                x2={sx}
                y2={VIEW_H}
                stroke={major ? "#cbd5e1" : "#eef2f6"}
                strokeWidth={1}
                pointerEvents="none"
              />
            );
          })}
          {gridY.map((y) => {
            const sy = worldToScreen({ x: 0, y }).y;
            const major = y % 5 === 0;
            return (
              <line
                key={`gy-${y}`}
                x1={0}
                y1={sy}
                x2={VIEW_W}
                y2={sy}
                stroke={major ? "#cbd5e1" : "#eef2f6"}
                strokeWidth={1}
                pointerEvents="none"
              />
            );
          })}

          {vertices.length >= 3 && (
            <polygon
              points={polygonPoints}
              fill="rgba(59,130,246,0.08)"
              stroke="#2563eb"
              strokeWidth={2}
              pointerEvents="none"
            />
          )}
          {vertices.length === 2 && (
            <line
              x1={worldToScreen(vertices[0]).x}
              y1={worldToScreen(vertices[0]).y}
              x2={worldToScreen(vertices[1]).x}
              y2={worldToScreen(vertices[1]).y}
              stroke="#2563eb"
              strokeWidth={2}
              pointerEvents="none"
            />
          )}

          {editing && lastScreen && hoverScreen && (
            <line
              x1={lastScreen.x}
              y1={lastScreen.y}
              x2={hoverScreen.x}
              y2={hoverScreen.y}
              stroke="#94a3b8"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              pointerEvents="none"
            />
          )}

          {vertices.map((v, i) => {
            const s = worldToScreen(v);
            return (
              <circle
                key={i}
                cx={s.x}
                cy={s.y}
                r={6}
                fill={dragging === i ? "#1d4ed8" : "white"}
                stroke="#1d4ed8"
                strokeWidth={2}
                style={{ cursor: editing ? "grab" : "default" }}
                onPointerDown={(e) => handleVertexDown(i, e)}
              />
            );
          })}

          {editing && snapScreen && (
            <rect
              x={snapScreen.x - 9}
              y={snapScreen.y - 9}
              width={18}
              height={18}
              fill="none"
              stroke="#16a34a"
              strokeWidth={2}
              pointerEvents="none"
            />
          )}
        </svg>

        {editing && hoverFree && (
          <div
            className="pointer-events-none absolute z-10 rounded border border-slate-300 bg-white/95 px-2 py-1 text-xs shadow"
            style={{ left: pointer.left, top: pointer.top }}
          >
            <p className="text-slate-700">
              {fmt(hoverFree.x)}, {fmt(hoverFree.y)} m
            </p>
            {last && (
              <p className="font-medium text-slate-900">
                L = {fmt(liveLength)} m · θ = {fmt(liveAngle)}°
              </p>
            )}
            <p className="text-slate-500">
              {mode === "polar" ? "Polar" : "Coordenada"}
              {commandBuffer && ` · ${commandBuffer}`}
            </p>
          </div>
        )}
      </div>

      <div className={`mt-3 grid gap-3 text-sm md:grid-cols-2${editingControlsClass}`}>
        <div className="rounded bg-slate-50 p-3 text-slate-600">
          {editing ? (
            <>
              <p>
                Teclado (con el puntero sobre el canvas): dígitos / . / - arman
                el comando · <b>Enter</b> agrega · <b>Esc</b> sale · <b>P</b>{" "}
                polar · <b>C</b> coordenada.
              </p>
              <p className="mt-1 text-slate-500">
                El cursor es libre; el snap se aplica al hacer click.
              </p>
            </>
          ) : (
            <p>
              Modo lectura — click en el canvas o «Editar» para volver a editar.
            </p>
          )}
        </div>

        <form onSubmit={handleCommandSubmit} className="space-y-2">
          <div className="flex gap-1">
            <button
              type="button"
              onClick={() => setMode("polar")}
              disabled={!editing}
              className={`rounded px-3 py-1 text-xs font-medium ${
                mode === "polar"
                  ? "bg-slate-900 text-white"
                  : "border border-slate-300 text-slate-700"
              }`}
            >
              Polar
            </button>
            <button
              type="button"
              onClick={() => setMode("coord")}
              disabled={!editing}
              className={`rounded px-3 py-1 text-xs font-medium ${
                mode === "coord"
                  ? "bg-slate-900 text-white"
                  : "border border-slate-300 text-slate-700"
              }`}
            >
              Coordenada
            </button>
          </div>
          <div className="flex gap-2">
            <input
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              disabled={!editing}
              placeholder={
                mode === "polar" ? "ángulo-largo (90-5)" : "x-y (2-5)"
              }
              className="w-full rounded border border-slate-300 px-2 py-1"
            />
            <button
              type="submit"
              disabled={!editing}
              className="rounded bg-slate-900 px-3 py-1 text-sm font-semibold text-white"
            >
              Agregar
            </button>
          </div>
          {message && <p className="text-xs text-red-600">{message}</p>}
        </form>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-4 text-sm">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={snapGrid}
            onChange={(e) => setSnapGrid(e.target.checked)}
          />
          Snap grilla al click ({GRID_SIZE} m)
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={snapVertex}
            onChange={(e) => setSnapVertex(e.target.checked)}
          />
          Object snap ({OSNAP_TOL} m)
        </label>
        <button
          type="button"
          onClick={undo}
          disabled={!editing}
          className="rounded border border-slate-300 px-3 py-1"
        >
          Deshacer
        </button>
        <button
          type="button"
          onClick={clear}
          disabled={!editing}
          className="rounded border border-slate-300 px-3 py-1"
        >
          Limpiar
        </button>
      </div>
    </section>
  );
}
