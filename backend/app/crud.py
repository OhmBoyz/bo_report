from sqlalchemy.orm import Session
from . import models, schemas
from .models import MainItem
from typing import List, Tuple

# Exemple: obtenir tous les MainItem
def get_main_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MainItem).offset(skip).limit(limit).all()

# Exemple: créer un MainItem
def create_main_item(db: Session, item: schemas.MainItemCreate):
    db_item = models.MainItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_backlog_item(db: Session, item: schemas.BacklogItemCreate):
    db_item = models.BacklogItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_items_by_go(db: Session, go_item: str):
    return db.query(MainItem).filter(MainItem.go_item == go_item).all()

def get_next_go_batch(db: Session, limit: int):
    # ex. trie par redcon_status croissant
    return (db.query(MainItem.go_item)
              .order_by(MainItem.redcon_status)
              .distinct()
              .limit(limit)
              .all())

# Récupère un MainItem par clé
def get_main_item(db: Session, go_item: str, part_number: str) -> models.MainItem | None:
    return (
        db.query(models.MainItem)
          .filter(
              models.MainItem.go_item == go_item,
              models.MainItem.part_number == part_number
          )
          .first()
    )

# Retourne toutes les clés (go_item, part_number) existantes
def get_all_main_keys(db: Session) -> List[Tuple[str, str]]:
    return (
        db.query(models.MainItem.go_item, models.MainItem.part_number)
          .all()
    )

# Met à jour un MainItem existant selon le dict data
def update_main_item(
    db: Session,
    db_obj: models.MainItem,
    data: dict
) -> models.MainItem:
    for key, value in data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Supprime un MainItem par clé
def delete_main_item(db: Session, go_item: str, part_number: str) -> None:
    db.query(models.MainItem).filter(
          models.MainItem.go_item == go_item,
          models.MainItem.part_number == part_number
      ).delete(synchronize_session=False)
    db.commit()

    # app/crud.py
def get_next_go_batch(db: Session, limit: int):
    return (
        db.query(MainItem.go_item)
          .filter(MainItem.pick_status == "NOT STARTED")  # <-- ajoute cette ligne
          .order_by(MainItem.redcon_status.asc())
          .distinct()
          .limit(limit)
          .all()
    )

# ---------- RapportLog ----------
def create_rapport_log(db: Session, log: schemas.RapportLogBase):
    db_obj = models.RapportLog(**log.dict())
    db.add(db_obj); db.commit(); db.refresh(db_obj)
    return db_obj

def list_rapport_logs(db: Session, skip=0, limit=100):
    return db.query(models.RapportLog).order_by(models.RapportLog.generated_at.desc())\
             .offset(skip).limit(limit).all()

# ---------- PrintLog ----------
def create_print_log(db: Session, log: schemas.PrintLogBase):
    db_obj = models.PrintLog(**log.dict())
    db.add(db_obj); db.commit(); db.refresh(db_obj)
    return db_obj

def list_print_logs(db: Session, skip=0, limit=100):
    return db.query(models.PrintLog).order_by(models.PrintLog.printed_at.desc())\
             .offset(skip).limit(limit).all()