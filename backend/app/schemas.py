from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from typing import List

class MainItemBase(BaseModel):
    go_item: str
    oracle: Optional[str] = ""
    item_number: Optional[str] = ""        # ← NOUVEAU
    discrete_job: Optional[str] = ""       # ← NOUVEAU
    part_number: str
    qty_req: int
    amo_qty: int = 0
    surplus_qty: int = 0
    kb_qty: int = 0
    flow_status: str = "AWAITING_SHIPPING"
    redcon_status: int = 0
    pick_status: str = "NOT STARTED"
    qty_remaining: Optional[int] = None
    shipping_info: Optional[str] = ""
    last_import_date: date

class MainItemCreate(MainItemBase):
    pass

class MainItem(MainItemBase):
    id: int

    class Config:
        orm_mode = True

class BacklogItemBase(BaseModel):
    go_item: str
    discrete: Optional[str]
    qty: int
    import_date: date

class BacklogItemCreate(BacklogItemBase):
    pass

class BacklogItem(BacklogItemBase):
    id: int
    class Config:
        orm_mode = True

class ReportItem(BaseModel):
    part_number: str
    qty_req: int
    qty_remaining: Optional[int]
    discrete: Optional[str]
    flow_status: Optional[str]
    
class Report(BaseModel):
    go_item: str
    generated_at: datetime
    items: List[ReportItem]

class PicklistItem(BaseModel):
    flow_status: str
    item: str
    discrete: str
    part_number: str
    qty_to_pick: int
    amo_qty: int
    kb_qty: int
    surplus_qty: int

class Picklist(BaseModel):
    go_item: str
    generated_at: datetime
    items: List[PicklistItem]

class RapportLogBase(BaseModel):
    go_item: str
    generated_at: datetime
    lines_json: str          # stocké tel quel en DB

class RapportLog(RapportLogBase):
    id: int
    class Config: from_attributes = True

class PrintLogBase(BaseModel):
    rapport_id: int
    printed_at: datetime
    reprint: bool = False

class PrintLog(PrintLogBase):
    id: int
    class Config: from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        from_attributes = True