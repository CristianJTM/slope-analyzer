import type { AnalysisRecord } from "../api/types";

export default function ResultPanel({
  record,
}: {
  record: AnalysisRecord | null;
}) {
  if (!record) {
    return <p className="text-slate-500">Sin resultados todavía.</p>;
  }

  const { result } = record;

  return (
    <div className="rounded border border-slate-200 p-4">
      <p className="text-sm text-slate-500">Factor de seguridad (FS)</p>
      <p className="text-4xl font-bold text-slate-900">{result.fs.toFixed(4)}</p>
      <p className="mt-2 text-sm text-slate-600">
        Método: {record.method}
        {result.iterations !== null && ` · iteraciones: ${result.iterations}`}
        {result.converged !== null &&
          ` · convergió: ${result.converged ? "sí" : "no"}`}
      </p>
    </div>
  );
}
