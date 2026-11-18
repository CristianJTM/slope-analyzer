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

export interface SearchBounds {
  x_min: number;
  x_max: number;
  y_min: number;
  y_max: number;
}

export interface SearchRequest {
  method: Method;
  geometry: SlopeGeometry;
  soil: SoilParams;
  num_slices: number;
  grid?: number;
  depths?: number[];
  bounds?: SearchBounds;
}

export interface CriticalCircle {
  fs: number;
  slip_circle: SlipCircle;
  method: string;
  num_slices: number;
  evaluations: number;
}
