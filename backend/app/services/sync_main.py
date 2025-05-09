# backend/app/services/sync_main.py
import math
from typing import Dict, Set, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from .data_import import read_backlog_df, read_redcon_df
from .utils import _find_column
from .. import crud, schemas


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _clean_str(v) -> str:
    """None/NaN → '' •  12.0 → '12' • sinon str(v)"""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def _safe_int(v, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


# --------------------------------------------------------------------------- #
def sync_main(db: Session, backlog_xlsx: str, redcon_xlsx: str) -> Dict[str, int]:
    """
    Fusion BACKLOG + REDCON → table main_item
    On **garde uniquement** les lignes présentes dans LES DEUX rapports.
    """
    # ============================= BACKLOG ================================= #
    bl_raw = read_backlog_df(backlog_xlsx)

    c_go   = _find_column(bl_raw.columns, "GO")
    c_it   = _find_column(bl_raw.columns, "Item")
    c_pr   = _find_column(bl_raw.columns, "Product ID")
    c_qty  = _find_column(bl_raw.columns, "Qty")
    c_shop = _find_column(bl_raw.columns, "Shop Order")
    c_orabl = _find_column(bl_raw.columns, "oracleordernum")

    mask = bl_raw[c_it].astype(str).str.match(r"^\d{2,3}[SW]\d?$", na=False)
    bl = bl_raw[mask].copy()

    bl["go_item"]      = bl[c_go].astype(str) + "-" + bl[c_it].astype(str)
    bl["item_number"]  = bl[c_it].apply(_clean_str)
    bl["part_number"]  = bl[c_pr].astype(str).str.rstrip(".")
    bl["qty_req"]      = bl[c_qty].fillna(0).astype(int)
    bl["discrete_job"] = bl[c_shop].apply(_clean_str)
    bl["oracle_bl"]    = bl[c_orabl].apply(_clean_str)

    bl = bl.set_index(["go_item", "part_number"])
    key_bl: Set[Tuple[str, str]] = set(bl.index)

    # ============================= REDCON ================================== #
    rc_raw = read_redcon_df(redcon_xlsx)

    cg = _find_column(rc_raw.columns, "GO ITEM")
    cp = _find_column(rc_raw.columns, "PART NUMBER")
    cq = _find_column(rc_raw.columns, "QTY REQD")
    cs = _find_column(rc_raw.columns, "BOH SURPLUS")
    ck = _find_column(rc_raw.columns, "KB SIZE")
    cr = _find_column(rc_raw.columns, "REDCON")
    cf = _find_column(rc_raw.columns, "FLOW STATUS")
    co = _find_column(rc_raw.columns, "ORACLE NUMBER")

    rc_norm = pd.DataFrame({
        "go_item":       rc_raw[cg].astype(str),
        "part_number":   rc_raw[cp].astype(str).str.rstrip("."),
        "qty_req_rc":    rc_raw[cq].fillna(0).astype(int),
        "surplus_qty":   rc_raw[cs].fillna(0).astype(int),
        "kb_qty":        rc_raw[ck].fillna(0).astype(int),
        "redcon_status": rc_raw[cr].fillna(0).astype(int),
        "flow_status":   rc_raw[cf].fillna("AWAITING_SHIPPING").astype(str),
        "oracle_rc":     rc_raw[co].apply(_clean_str),
    })

    rc_norm = (
        rc_norm.sort_values(["go_item", "part_number"])
               .groupby(["go_item", "part_number"], as_index=False)
               .last()
               .set_index(["go_item", "part_number"])
    )
    key_rc: Set[Tuple[str, str]] = set(rc_norm.index)

    # ========================== INTERSECTION =============================== #
    keys_common: Set[Tuple[str, str]] = key_bl & key_rc

    created = updated = deleted = 0

    for key in keys_common:
        go_item, part_number = key
        bl_row = bl.loc[key]
        rc_row = rc_norm.loc[key]

        qty_req = int(bl_row["qty_req"])

        oracle = (
            _clean_str(bl_row["oracle_bl"])
            or _clean_str(rc_row["oracle_rc"])
        )
        item_number = _clean_str(bl_row["item_number"]) or go_item.split("-")[1]
        discrete    = _clean_str(bl_row["discrete_job"])
        flow_stat   = _clean_str(rc_row["flow_status"]) or "AWAITING_SHIPPING"

        redcon  = _safe_int(rc_row["redcon_status"])
        surplus = _safe_int(rc_row["surplus_qty"])
        kb_qty  = _safe_int(rc_row["kb_qty"])

        payload = {
            "go_item":       go_item,
            "oracle":        oracle,
            "item_number":   item_number,
            "discrete_job":  discrete,
            "part_number":   part_number,
            "qty_req":       qty_req,
            "amo_qty":       0,
            "surplus_qty":   surplus,
            "kb_qty":        kb_qty,
            "flow_status":   flow_stat,
            "redcon_status": redcon,
            "qty_remaining": qty_req,
            "shipping_info": "",
            "last_import_date": pd.Timestamp.today().date(),
        }

        db_obj = crud.get_main_item(db, go_item, part_number)
        if db_obj:
            payload["pick_status"] = db_obj.pick_status
            crud.update_main_item(db, db_obj, payload)
            updated += 1
        else:
            payload["pick_status"] = "NOT STARTED"
            crud.create_main_item(db, schemas.MainItemCreate(**payload))
            created += 1

    # ============================ PURGE =================================== #
    for go_item, part_number in set(crud.get_all_main_keys(db)) - keys_common:
        crud.delete_main_item(db, go_item, part_number)
        deleted += 1

    return {"created": created, "updated": updated, "deleted": deleted}
