# backend/app/services/picklist_service.py

from __future__ import annotations
import json
from datetime import datetime
from typing import List, Dict, Literal, Optional, Tuple

from sqlalchemy.orm import Session

from app import crud, models, schemas


def _clean_discrete(val: Optional[str]) -> str:
    """Supprime 'NAN', 'SQU' ou None."""
    if not val:
        return ""
    up = val.upper()
    return "" if up in ("NAN", "SQU") else val


def _clean_part(val: Optional[str]) -> str:
    """Supprime un éventuel point final."""
    return (val or "").rstrip('.')


def _clean_flow(fs: Optional[str]) -> str:
    """Remplace None/nan par AWAITING_SHIPPING"""
    if not fs or str(fs).lower() == "nan":
        return "AWAITING_SHIPPING"
    return fs


def _select_next_job(db: Session) -> Tuple[Optional[str], List[models.MainItem]]:
    """
    Sélectionne le prochain job (préfixe GO) à imprimer selon le plus petit redcon_status
    parmi les lignes NOT STARTED.

    Renvoie (go_prefix, liste des MainItem correspondants).
    """
    first = (
        db.query(models.MainItem)
          .filter(models.MainItem.pick_status == "NOT STARTED")
          .order_by(models.MainItem.redcon_status)
          .first()
    )
    if not first:
        return None, []
    go_prefix = first.go_item[:10]
    lines = (
        db.query(models.MainItem)
          .filter(
              models.MainItem.go_item.like(f"{go_prefix}%"),
              models.MainItem.pick_status == "NOT STARTED"
          )
          .all()
    )
    return go_prefix, lines


def generate_picklists(
    db: Session,
    mode: Literal["batch", "go"],
    qty_jobs: int | None = None,
    go_number: str | None = None,
) -> List[Dict]:
    """
    Génère une ou plusieurs picklists :
    - mode 'batch' : prend les 'qty_jobs' prochains jobs
    - mode 'go'    : pour un GO précis

    Met à jour pick_status à PICKING et renvoie une liste de dictionnaires :
      {go_item, generated_at, items: [...]}
    """
    results: List[Dict] = []
    done = 0

    while True:
        if mode == "batch":
            if done >= (qty_jobs or 1):
                break
            go, rows = _select_next_job(db)
            if not rows:
                break
        else:
            if done > 0:
                break
            go = go_number
            rows = (
                db.query(models.MainItem)
                  .filter(models.MainItem.go_item.like(f"{go}%"))
                  .all()
            )
        if not rows:
            break

        lines: List[Dict] = []
        for r in rows:
            lines.append({
                "flow_status": _clean_flow(r.flow_status),
                "item":        r.item_number or "",
                "discrete":    r.discrete_job or "",
                "part_number": r.part_number,
                "qty_to_pick": r.qty_remaining or r.qty_req,
                "amo_qty":     r.amo_qty,
                "kb_qty":      r.kb_qty,
                "surplus_qty": r.surplus_qty,
            })
            crud.update_main_item(db, r, {"pick_status": "PICKING"})

        results.append({
            "go_item":      go,
            "generated_at": datetime.utcnow(),
            "items":        lines,
        })
        done += 1
        if mode == "go":
            break

    return results


def _latest_logged_picklist(
    db: Session,
    go_item: str
) -> Optional[schemas.Picklist]:
    """
    Si une picklist a déjà été générée et loggée (dans rapport_log),
    récupère sa dernière version et la renvoie sous forme de schemas.Picklist.
    """
    log = (
        db.query(models.RapportLog)
          .filter(models.RapportLog.go_item == go_item)
          .order_by(models.RapportLog.generated_at.desc())
          .first()
    )
    if not log:
        return None

    raw_lines = json.loads(log.lines_json)
    items: List[schemas.PicklistItem] = []
    for l in raw_lines:
        items.append(schemas.PicklistItem(
            flow_status=_clean_flow(l.get("flow_status")),
            item=l.get("item", ""),
            discrete=_clean_discrete(l.get("discrete")),
            part_number=_clean_part(l.get("part_number")),
            qty_to_pick=l.get("qty_to_pick", 0),
            amo_qty=l.get("amo_qty", 0),
            kb_qty=l.get("kb_qty", 0),
            surplus_qty=l.get("surplus_qty", 0),
        ))

    return schemas.Picklist(
        go_item=go_item,
        generated_at=log.generated_at,
        items=items
    )


def get_picklist_for_go(
    db: Session,
    go_item: str
) -> schemas.Picklist:
    """
    Renvoie une picklist pour un GO :
    - si déjà loggée → _latest_logged_picklist
    - sinon reconstitue "à la volée" à partir des lignes NOT STARTED
    """
    logged = _latest_logged_picklist(db, go_item)
    if logged:
        return logged

    rows = (
        db.query(models.MainItem)
          .filter(
              models.MainItem.go_item.like(f"{go_item}%"),
              models.MainItem.pick_status == "NOT STARTED"
          )
          .all()
    )
    items: List[schemas.PicklistItem] = []
    for r in rows:
        items.append(schemas.PicklistItem(
            flow_status=_clean_flow(r.flow_status),
            item=r.item_number or "",
            discrete=_clean_discrete(r.discrete_job),
            part_number=_clean_part(r.part_number),
            qty_to_pick=r.qty_remaining if r.qty_remaining is not None else r.qty_req,
            amo_qty=r.amo_qty,
            kb_qty=r.kb_qty,
            surplus_qty=r.surplus_qty,
        ))

    return schemas.Picklist(
        go_item=go_item,
        generated_at=datetime.utcnow(),
        items=items
    )


def get_picklists_batch(
    db: Session,
    qty_jobs: int
) -> List[schemas.Picklist]:
    """
    Renvoie les picklists pour les prochains jobs (batch).
    Ce sont les mêmes GO préfixes sélectionnés par get_next_go_batch.
    """
    raw = generate_picklists(db, mode="batch", qty_jobs=qty_jobs)
    return [schemas.Picklist(**r) for r in raw]
