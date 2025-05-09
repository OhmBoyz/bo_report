from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import SessionLocal
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/items",   # toutes les routes démarrent par /items
    tags=["items"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.MainItem])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_main_items(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.MainItem)
def create_item(item: schemas.MainItemCreate, db: Session = Depends(get_db)):
    return crud.create_main_item(db, item)     

@router.patch("/{go_item}/{part_number}", response_model=schemas.MainItem, dependencies=[Depends(get_current_user)])
def update_item(
    go_item: str,
    part_number: str,
    patch: dict,                         # ex. {"pick_status":"FINISHED","qty_remaining":0}
    db: Session = Depends(get_db)
):
    db_obj = crud.get_main_item(db, go_item, part_number)
    if not db_obj:
        raise HTTPException(404, "Line not found")
    return crud.update_main_item(db, db_obj, patch)