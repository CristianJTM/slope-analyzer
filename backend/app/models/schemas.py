from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SlopeGeometryIn(BaseModel):
    height: float = Field(gt=0)
    angle: float


class SlipCircleIn(BaseModel):
    center_x: float
    center_y: float
    radius: float = Field(gt=0)


class SoilParamsIn(BaseModel):
    cohesion: float = Field(ge=0)
    phi: float = Field(ge=0)
    gamma: float = Field(gt=0)
    ru: float = Field(0.0, ge=0)


class AnalyzeRequest(BaseModel):
    method: Literal["bishop", "fellenius"]
    geometry: SlopeGeometryIn
    slip_circle: SlipCircleIn
    soil: SoilParamsIn
    num_slices: int = Field(50, ge=1)


class AnalysisResponse(BaseModel):
    id: int
    method: str
    created_at: datetime
    input: dict
    result: dict


class SearchBoundsIn(BaseModel):
    x_min: float
    x_max: float
    y_min: float
    y_max: float


class SearchRequest(BaseModel):
    method: Literal["bishop", "fellenius"]
    geometry: SlopeGeometryIn
    soil: SoilParamsIn
    num_slices: int = Field(50, ge=1)
    grid: int = Field(15, ge=2)
    depths: list[float] = Field(default_factory=lambda: [0.0])
    bounds: SearchBoundsIn | None = None


class CriticalCircleResponse(BaseModel):
    fs: float
    slip_circle: SlipCircleIn
    method: str
    num_slices: int
    evaluations: int
