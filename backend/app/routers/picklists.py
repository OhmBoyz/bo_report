# app/routers/picklists.py
from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Literal, List, Dict

from fastapi import APIRouter, Depends, HTTPException, Path as PathParam
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session
from weasyprint import HTML

from app import crud, models, schemas
from app.database import get_db
from app.services.picklist_service import (
    generate_picklists,
    get_picklist_for_go,
    get_picklists_batch,
)
from app.services.utils import load_logo_base64

# ---------------------------------------------------------------------------
LOGO_PATH = Path(__file__).resolve().parent.parent / "static" / "eaton_logo.png"
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=select_autoescape(["html"]),
)

router = APIRouter(prefix="/picklists", tags=["picklists"])


def _clean_flow(val: str | None) -> str:
    """Remplace None/nan/'' par chaîne vide pour l’affichage."""
    if not val:
        return ""
    return "" if str(val).lower() == "nan" else val


# Modèle de requête
class BatchRequest(schemas.BaseModel):
    mode: Literal["batch", "go"]
    qty_jobs: int | None = None
    go_number: str | None = None


@router.post("/generate")
def generate(req: BatchRequest, db: Session = Depends(get_db)):
    """
    1) Génère une ou plusieurs pick-lists.
    2) Les enregistre dans `rapport_log`.
    3) Renvoie la structure prête à être affichée.
    """
    if req.mode == "batch" and not req.qty_jobs:
        raise HTTPException(400, "qty_jobs obligatoire en mode batch")
    if req.mode == "go" and not req.go_number:
        raise HTTPException(400, "go_number obligatoire en mode go")

    # 1) génération des pick‑lists
    picks: List[Dict] = generate_picklists(
        db,
        mode=req.mode,
        qty_jobs=req.qty_jobs,
        go_number=req.go_number,
    )

    # 2) journalisation dans rapport_log
    #    on utilise désormais pl["items"] (pas pl["lines"]) :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
    for pl in picks:
        crud.create_rapport_log(
            db,
            schemas.RapportLogBase(
                go_item      = pl["go_item"],
                generated_at = pl["generated_at"],
                lines_json   = json.dumps(pl["items"], separators=(",", ":")),
            ),
        )

    return picks


@router.get("/go/{go_item}", response_model=schemas.Picklist)
def picklist_go(go_item: str = PathParam(...), db: Session = Depends(get_db)):
    return get_picklist_for_go(db, go_item)


@router.get("/batch/{qty_jobs}", response_model=List[schemas.Picklist])
def picklist_batch(qty_jobs: int, db: Session = Depends(get_db)):
    return get_picklists_batch(db, qty_jobs)


@router.get("/pdf/{go_item}", summary="PDF paysage de la pick-list")
def picklist_pdf(go_item: str, db: Session = Depends(get_db)):
    # Reconstitution de la pick‑list
    pick = get_picklist_for_go(db, go_item)
    # Chargement du logo
    logo64 = load_logo_base64(LOGO_PATH)
    # Récupération du premier oracle trouvé pour ce GO
    first = (
        db.query(models.MainItem)
          .filter(models.MainItem.go_item.like(f"{go_item}%"))
          .first()
    )
    oracle = first.oracle if first else ""
    # Rendu du template HTML
    tpl = templates.get_template("picklist.html")
    html_str = tpl.render(
        logo64       = logo64,
        go_item      = pick.go_item,
        oracle       = oracle,
        generated_at = pick.generated_at,
        lines        = [
            {**l.dict(), "flow_status": _clean_flow(l.flow_status)}
            for l in pick.items
        ],
    )
    # Génération du PDF
    pdf_bytes = HTML(string=html_str).write_pdf()
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f'inline; filename="picklist_{go_item}.pdf"'
        },
    )
