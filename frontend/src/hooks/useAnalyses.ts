import { useCallback, useEffect, useState } from "react";
import { analyze, listAnalyses } from "../api/analysis";
import type { AnalysisRecord, AnalyzeRequest } from "../api/types";

export function useAnalyses() {
  const [history, setHistory] = useState<AnalysisRecord[]>([]);
  const [result, setResult] = useState<AnalysisRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setHistory(await listAnalyses());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al cargar historial");
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const runAnalysis = useCallback(
    async (req: AnalyzeRequest) => {
      setLoading(true);
      setError(null);
      try {
        const record = await analyze(req);
        setResult(record);
        await refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Error al calcular");
      } finally {
        setLoading(false);
      }
    },
    [refresh],
  );

  return { history, result, loading, error, runAnalysis, refresh };
}
