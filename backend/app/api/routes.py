from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models.schemas import AnalysisResponse, AnalyzeRequest
from ..services.analysis import get_analyses, run_analysis

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse, status_code=201)
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    return run_analysis(req, db)


@router.get("/analyses", response_model=list[AnalysisResponse])
def analyses(db: Session = Depends(get_db)):
    return get_analyses(db)
