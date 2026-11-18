import type { CriticalCircle } from "../api/types";

export default function CriticalCirclePanel({
  circle,
}: {
  circle: CriticalCircle | null;
}) {
  if (!circle) {
    return (
      <p className="text-slate-500">Todavía no buscaste el círculo crítico.</p>
    );
  }

  const { slip_circle } = circle;

  return (
    <div className="rounded border border-slate-200 p-4">
      <p className="text-sm text-slate-500">FS mínimo (círculo crítico)</p>
      <p className="text-4xl font-bold text-slate-900">{circle.fs.toFixed(4)}</p>
      <p className="mt-2 text-sm text-slate-600">
        Centro ({slip_circle.center_x.toFixed(3)},{" "}
        {slip_circle.center_y.toFixed(3)}) m · R {slip_circle.radius.toFixed(3)} m
        · evaluaciones: {circle.evaluations}
      </p>
    </div>
  );
}
