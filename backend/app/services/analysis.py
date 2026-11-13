from sqlalchemy.orm import Session

from ..core.bishop import bishop_fs
from ..core.fellenius import fellenius_fs
from ..core.models import SlipCircle, SlopeGeometry, SoilParams
from ..core.slicing import slice_slope
from ..db.repository import create_analysis, list_analyses
from ..models.schemas import AnalysisResponse, AnalyzeRequest


def run_analysis(req: AnalyzeRequest, db: Session) -> AnalysisResponse:
    geometry = SlopeGeometry(height=req.geometry.height, angle=req.geometry.angle)
    circle = SlipCircle(
        center_x=req.slip_circle.center_x,
        center_y=req.slip_circle.center_y,
        radius=req.slip_circle.radius,
    )
    soil = SoilParams(
        cohesion=req.soil.cohesion,
        phi=req.soil.phi,
        gamma=req.soil.gamma,
        ru=req.soil.ru,
    )
    slices = slice_slope(geometry, circle, num_slices=req.num_slices)

    if req.method == "bishop":
        result = bishop_fs(slices, soil)
        result_data = {
            "fs": result.fs,
            "iterations": result.iterations,
            "converged": result.converged,
        }
    else:
        result_data = {
            "fs": fellenius_fs(slices, soil),
            "iterations": None,
            "converged": None,
        }

    record = create_analysis(db, req.method, req.model_dump(), result_data)
    return AnalysisResponse(
        id=record.id,
        method=record.method,
        created_at=record.created_at,
        input=record.input,
        result=record.result,
    )


def get_analyses(db: Session) -> list[AnalysisResponse]:
    return [
        AnalysisResponse(
            id=record.id,
            method=record.method,
            created_at=record.created_at,
            input=record.input,
            result=record.result,
        )
        for record in list_analyses(db)
    ]
