from pydantic import BaseModel
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

class BatchRequest(BaseModel):
    qty_jobs: int

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.post("/go/{go_item}", response_model=schemas.Report)
def report_go(
    go_item: str = Path(..., description="GO à rapporter"),
    db: Session = Depends(get_db)
):
    items = crud.get_items_by_go(db, go_item)
    report_items = [
        schemas.ReportItem(
            part_number=i.part_number,
            qty_req=i.qty_req,
            qty_remaining=i.qty_remaining,
            discrete=i.discrete,
            flow_status=i.flow_status
        ) for i in items
    ]
    return schemas.Report(
        go_item=go_item,
        generated_at=datetime.utcnow(),
        items=report_items
    )

@router.post("/batch", response_model=List[schemas.Report])
def report_batch(
    req: BatchRequest,
    db: Session = Depends(get_db)
):
    # Récupère les prochains GO à traiter
    go_list = crud.get_next_go_batch(db, req.qty_jobs)
    reports: List[schemas.Report] = []
    for (go_item,) in go_list:
        # Récupère toutes les lignes associées à ce GO
        items = crud.get_items_by_go(db, go_item)
        # Transforme en objets ReportItem
        report_items = [
            schemas.ReportItem(
                part_number=i.part_number,
                qty_req=i.qty_req,
                qty_remaining=i.qty_remaining,
                discrete=i.discrete,
                flow_status=i.flow_status
            ) for i in items
        ]
        # Compose le rapport
        reports.append(
            schemas.Report(
                go_item=go_item,
                generated_at=datetime.utcnow(),
                items=report_items
            )
        )
    return reports