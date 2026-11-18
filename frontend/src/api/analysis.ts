import { request } from "./client";
import type {
  AnalysisRecord,
  AnalyzeRequest,
  CriticalCircle,
  SearchRequest,
} from "./types";

export function analyze(req: AnalyzeRequest): Promise<AnalysisRecord> {
  return request<AnalysisRecord>("/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
}

export function listAnalyses(): Promise<AnalysisRecord[]> {
  return request<AnalysisRecord[]>("/analyses");
}

export function searchCriticalCircle(req: SearchRequest): Promise<CriticalCircle> {
  return request<CriticalCircle>("/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
}
