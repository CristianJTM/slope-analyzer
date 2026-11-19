import CriticalCirclePanel from "./components/CriticalCirclePanel";
import HistoryList from "./components/HistoryList";
import ResultPanel from "./components/ResultPanel";
import SlopeEditor from "./components/SlopeEditor";
import SlopeForm from "./components/SlopeForm";
import { useAnalyses } from "./hooks/useAnalyses";

export default function App() {
  const {
    history,
    result,
    criticalCircle,
    loading,
    searching,
    error,
    runAnalysis,
    runSearch,
  } = useAnalyses();

  return (
    <main className="mx-auto max-w-5xl p-6">
      <h1 className="text-2xl font-bold text-slate-900">slope-analyzer</h1>
      <p className="mb-6 text-sm text-slate-500">
        Análisis de estabilidad de taludes — Bishop y Fellenius
      </p>

      {error && (
        <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      <div className="mb-6">
        <SlopeEditor />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded border border-slate-200 p-4">
          <h2 className="mb-3 text-lg font-semibold">Datos del talud</h2>
          <SlopeForm
            onAnalyze={runAnalysis}
            onSearch={runSearch}
            loading={loading}
            searching={searching}
          />
        </section>

        <section className="space-y-6">
          <div>
            <h2 className="mb-3 text-lg font-semibold">Resultado (círculo dado)</h2>
            <ResultPanel record={result} />
          </div>
          <div>
            <h2 className="mb-3 text-lg font-semibold">Círculo crítico</h2>
            <CriticalCirclePanel circle={criticalCircle} />
          </div>
          <div>
            <h2 className="mb-3 text-lg font-semibold">Historial</h2>
            <HistoryList records={history} />
          </div>
        </section>
      </div>
    </main>
  );
}
