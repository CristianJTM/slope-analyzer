from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models.schemas import (
    AnalysisResponse,
    AnalyzeRequest,
    CriticalCircleResponse,
    SearchRequest,
)
from ..services.analysis import get_analyses, run_analysis, run_search

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse, status_code=201)
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    return run_analysis(req, db)


@router.get("/analyses", response_model=list[AnalysisResponse])
def analyses(db: Session = Depends(get_db)):
    return get_analyses(db)


@router.post("/search", response_model=CriticalCircleResponse)
def search(req: SearchRequest):
    return run_search(req)
