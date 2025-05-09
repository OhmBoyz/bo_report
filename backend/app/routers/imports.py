# backend/app/routers/imports.py
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from app.database import get_db
from app.services.data_import import read_backlog_df, read_redcon_df
from app.services.sync_main import sync_main
from app.services.utils import _find_column
from .. import crud, schemas
from app.routers.auth import get_current_user

router = APIRouter(prefix="/imports", tags=["imports"])

@router.post("/redcon", dependencies=[Depends(get_current_user)])
async def import_redcon(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    df = pd.read_excel(file.file, sheet_name='Export')
    count = 0
    for _, row in df.iterrows():
        # colonne repérage
        col_qty   = _find_column(df.columns, 'QTY REQD')
        col_red   = _find_column(df.columns, 'REDCON')
        col_go    = _find_column(df.columns, 'GO ITEM')
        col_part  = _find_column(df.columns, 'PART NUMBER')
        col_orac  = _find_column(df.columns, 'ORACLE NUMBER')
        col_flow  = _find_column(df.columns, 'FLOW STATUS')    # ← new
        # récupération et conversion sécurisée
        raw_qty = row[col_qty]
        try:
            qty_req = int(raw_qty)
        except Exception:
            qty_req = 0

        raw_red = row[col_red]
        try:
            redcon_status = int(raw_red)
        except Exception:
            redcon_status = 0
        
        flow_status = str(row[col_flow] or "AWAITING_SHIPPING")  # ← default if empty

        data = {
            'go_item':        str(row[col_go]),
            'part_number':    str(row[col_part]).rstrip('.'),
            'oracle':         str(row[col_orac]),
            'qty_req':        qty_req,
            'redcon_status':  redcon_status,
            'flow_status':    flow_status,                 # ← store it
            'discrete':       str(row.get('DISCRETE SUBINVENTORY', '') or ''),
            'last_import_date': pd.Timestamp.today().date()
        }

        crud.create_main_item(db, schemas.MainItemCreate(**data))
        count += 1

    return {"imported_redcon": count}

@router.post("/backlog", dependencies=[Depends(get_current_user)])
async def import_backlog(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    df = pd.read_excel(file.file, sheet_name='Sheet1')
    count = 0
    for _, row in df.iterrows():
        data = {

            # on récupère la colonne GO et la colonne Item pour construire le go_item
            'go_item': (
               str(row[_find_column(df.columns, 'GO')])
               + '-'
               + str(row[_find_column(df.columns, 'Item')])
            ),
            # discrete idem
            'discrete': str(row.get(_find_column(df.columns, 'Shop Order'), '')),
            'qty': int(row[_find_column(df.columns, 'Qty')]),
            'import_date': pd.Timestamp.today().date(),
            # **nouveau** : on prend la vraie colonne Part Number
            'part_number': (
               str(row[_find_column(df.columns, 'Product ID')])
               .rstrip('.')       # on vire un éventuel point final
            ),

        }
        crud.create_backlog_item(db, schemas.BacklogItemCreate(**data))
        count += 1
    return {"imported_backlog": count}

@router.post("/sync", dependencies=[Depends(get_current_user)])
async def full_sync(
    backlog_path: str,
    redcon_path: str,
    db: Session = Depends(get_db)
):
    # sync_main est synchrone, pas besoin de await
    result = sync_main(db, backlog_path, redcon_path)
    return result
