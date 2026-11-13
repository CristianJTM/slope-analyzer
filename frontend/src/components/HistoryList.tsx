import type { AnalysisRecord } from "../api/types";

export default function HistoryList({ records }: { records: AnalysisRecord[] }) {
  if (records.length === 0) {
    return <p className="text-slate-500">Todavía no hay corridas guardadas.</p>;
  }

  return (
    <ul className="divide-y divide-slate-200 rounded border border-slate-200">
      {records.map((record) => (
        <li
          key={record.id}
          className="flex items-center justify-between px-3 py-2 text-sm"
        >
          <span className="font-mono text-slate-500">#{record.id}</span>
          <span>{record.method}</span>
          <span className="font-semibold">FS {record.result.fs.toFixed(4)}</span>
          <span className="text-slate-500">
            {new Date(record.created_at).toLocaleString()}
          </span>
        </li>
      ))}
    </ul>
  );
}
