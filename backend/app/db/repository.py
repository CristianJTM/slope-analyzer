from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Analysis


def create_analysis(
    db: Session, method: str, input_data: dict, result: dict
) -> Analysis:
    record = Analysis(method=method, input=input_data, result=result)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_analyses(db: Session) -> list[Analysis]:
    return list(db.scalars(select(Analysis).order_by(Analysis.id)))
