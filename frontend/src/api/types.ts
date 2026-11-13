export type Method = "bishop" | "fellenius";

export interface SlopeGeometry {
  height: number;
  angle: number;
}

export interface SlipCircle {
  center_x: number;
  center_y: number;
  radius: number;
}

export interface SoilParams {
  cohesion: number;
  phi: number;
  gamma: number;
  ru: number;
}

export interface AnalyzeRequest {
  method: Method;
  geometry: SlopeGeometry;
  slip_circle: SlipCircle;
  soil: SoilParams;
  num_slices: number;
}

export interface AnalysisResult {
  fs: number;
  iterations: number | null;
  converged: boolean | null;
}

export interface AnalysisRecord {
  id: number;
  method: string;
  created_at: string;
  input: AnalyzeRequest;
  result: AnalysisResult;
}
