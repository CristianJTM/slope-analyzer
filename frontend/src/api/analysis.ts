import { request } from "./client";
import type { AnalysisRecord, AnalyzeRequest } from "./types";

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
