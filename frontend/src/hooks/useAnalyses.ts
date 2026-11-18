import { useCallback, useEffect, useState } from "react";
import { analyze, listAnalyses, searchCriticalCircle } from "../api/analysis";
import type {
  AnalysisRecord,
  AnalyzeRequest,
  CriticalCircle,
  SearchRequest,
} from "../api/types";

export function useAnalyses() {
  const [history, setHistory] = useState<AnalysisRecord[]>([]);
  const [result, setResult] = useState<AnalysisRecord | null>(null);
  const [criticalCircle, setCriticalCircle] = useState<CriticalCircle | null>(
    null,
  );
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
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

  const runSearch = useCallback(async (req: SearchRequest) => {
    setSearching(true);
    setError(null);
    try {
      setCriticalCircle(await searchCriticalCircle(req));
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Error al buscar el círculo crítico",
      );
    } finally {
      setSearching(false);
    }
  }, []);

  return {
    history,
    result,
    criticalCircle,
    loading,
    searching,
    error,
    runAnalysis,
    runSearch,
    refresh,
  };
}
