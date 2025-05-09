from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from datetime import datetime
import json

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/rapports", response_model=list[schemas.RapportLog])
def list_rapports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_rapport_logs(db, skip, limit)

@router.get("/prints", response_model=list[schemas.PrintLog])
def list_prints(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_print_logs(db, skip, limit)

@router.post("/prints")
def print_picklist(rapport_id: int, reprint: bool = False, db: Session = Depends(get_db)):
    # ici on ne génère pas encore le PDF ; on journalise simplement
    log = schemas.PrintLogBase(
        rapport_id = rapport_id,
        printed_at = datetime.utcnow(),
        reprint    = reprint
    )
    crud.create_print_log(db, log)
    return {"status":"logged"}
