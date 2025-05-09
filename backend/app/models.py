from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base
#from app.models import Base

Base = declarative_base()


class MainItem(Base):
    __tablename__ = "main_item"

    id            = Column(Integer, primary_key=True)
    go_item       = Column(String(30),  nullable=False)
    oracle        = Column(String(10))
    item_number   = Column(String(10))   # ← NOUVEAU
    discrete_job  = Column(String(50))   # ← NOUVEAU
    part_number   = Column(String(50),  nullable=False)
    qty_req       = Column(Integer,      nullable=False)
    amo_qty       = Column(Integer,      default=0)
    surplus_qty   = Column(Integer,      default=0)
    kb_qty        = Column(Integer,      default=0)
    flow_status   = Column(String(30))
    redcon_status = Column(Integer,      default=0)
    pick_status   = Column(String(15),   default="NOT STARTED")
    qty_remaining = Column(Integer,      default=0)
    shipping_info = Column(String(60))
    last_import_date = Column(Date,      nullable=False)

class BacklogItem(Base):
    __tablename__ = 'backlog_item'
    id = Column(Integer, primary_key=True)
    go_item = Column(String(20), nullable=False)
    item_number  = Column(String(10))
    discrete = Column(String(50))
    qty = Column(Integer)
    import_date = Column(Date, nullable=False)

# Classes complémentaires à ajouter selon besoins: FlagLog, RapportLog, PrintLog
class RapportLog(Base):
    __tablename__ = "rapport_log"
    id              = Column(Integer, primary_key=True)
    go_item         = Column(String(20), nullable=False)
    generated_at    = Column(DateTime, nullable=False)
    lines_json      = Column(String,  nullable=False)   # JSON compact des lignes

class PrintLog(Base):
    __tablename__ = "print_log"
    id            = Column(Integer, primary_key=True)
    rapport_id    = Column(Integer, nullable=False)     # FK → RapportLog.id (à ajouter si tu veux la contrainte)
    printed_at    = Column(DateTime, nullable=False)
    reprint       = Column(Boolean, default=False)

class PicklistLog(Base):
    __tablename__ = "picklist_log"
    id            = Column(Integer, primary_key=True)
    go_item       = Column(String(20), nullable=False)
    payload_json  = Column(Text, nullable=False)   # la pick‑list complète
    printed_at    = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)