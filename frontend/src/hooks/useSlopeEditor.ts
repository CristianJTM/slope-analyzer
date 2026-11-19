import { useCallback, useState } from "react";

export interface Point {
  x: number;
  y: number;
}

export type InputMode = "polar" | "coord";
export type SnapKind = "vertex" | "grid" | null;

export const GRID_SIZE = 1; // metros
export const OSNAP_TOL = 0.5; // metros
export const MIN_VERTICES = 6;

export function resolvePoint(
  raw: Point,
  vertices: Point[],
  opts: { snapGrid: boolean; snapVertex: boolean },
  excludeIndex?: number,
): { point: Point; snappedTo: SnapKind } {
  if (opts.snapVertex && vertices.length > 0) {
    let best: Point | null = null;
    let bestDist = OSNAP_TOL;
    for (let i = 0; i < vertices.length; i++) {
      if (i === excludeIndex) continue;
      const v = vertices[i];
      const d = Math.hypot(v.x - raw.x, v.y - raw.y);
      if (d <= bestDist) {
        bestDist = d;
        best = v;
      }
    }
    if (best) {
      return { point: best, snappedTo: "vertex" };
    }
  }
  if (opts.snapGrid) {
    return {
      point: {
        x: Math.round(raw.x / GRID_SIZE) * GRID_SIZE,
        y: Math.round(raw.y / GRID_SIZE) * GRID_SIZE,
      },
      snappedTo: "grid",
    };
  }
  return { point: raw, snappedTo: null };
}

function parseCommand(text: string): { a: number; b: number } | null {
  const match = text.trim().match(/^(-?\d+(?:\.\d+)?)-(-?\d+(?:\.\d+)?)$/);
  if (!match) return null;
  return { a: Number(match[1]), b: Number(match[2]) };
}

export function useSlopeEditor() {
  const [vertices, setVertices] = useState<Point[]>([]);
  const [mode, setMode] = useState<InputMode>("polar");
  const [snapGrid, setSnapGrid] = useState(true);
  const [snapVertex, setSnapVertex] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  const addVertex = useCallback((point: Point) => {
    setVertices((vs) => [...vs, point]);
  }, []);

  const moveVertex = useCallback((index: number, point: Point) => {
    setVertices((vs) => vs.map((v, i) => (i === index ? point : v)));
  }, []);

  const undo = useCallback(() => {
    setVertices((vs) => vs.slice(0, -1));
  }, []);

  const clear = useCallback(() => {
    setVertices([]);
    setMessage(null);
  }, []);

  const applyCommand = useCallback(
    (text: string) => {
      const parsed = parseCommand(text);
      if (!parsed) {
        setMessage("Comando inválido. Formato a-b (ej. 90-5 o 2-5).");
        return;
      }
      if (mode === "coord") {
        setVertices((vs) => [...vs, { x: parsed.a, y: parsed.b }]);
        setMessage(null);
        return;
      }
      if (parsed.b <= 0) {
        setMessage("La longitud debe ser mayor que 0.");
        return;
      }
      const radians = (parsed.a * Math.PI) / 180;
      setVertices((vs) => {
        const base = vs.length > 0 ? vs[vs.length - 1] : { x: 0, y: 0 };
        return [
          ...vs,
          {
            x: base.x + parsed.b * Math.cos(radians),
            y: base.y + parsed.b * Math.sin(radians),
          },
        ];
      });
      setMessage(null);
    },
    [mode],
  );

  return {
    vertices,
    mode,
    setMode,
    snapGrid,
    setSnapGrid,
    snapVertex,
    setSnapVertex,
    message,
    addVertex,
    moveVertex,
    undo,
    clear,
    applyCommand,
  };
}
