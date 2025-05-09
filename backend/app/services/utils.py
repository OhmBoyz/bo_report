# backend/app/services/utils.py
from pathlib import Path
from typing import Sequence
import base64

def _find_column(columns: Sequence[str], keyword: str) -> str:
    """Retourne le nom de colonne qui contient keyword (case-insensitive)."""
    keyword = keyword.lower()
    for col in columns:
        if keyword in col.lower():
            return col
    raise KeyError(f"Colonne contenant '{keyword}' non trouvée dans {list(columns)}")

def load_logo_base64(path: str = Path(__file__).resolve().parent.parent / "static" / "eaton_logo.png") -> str:
    """
    Renvoie une string 'data:image/png;base64,...' pour être
    insérée directement dans le <img src="..."> du HTML.
    """
    img_bytes = Path(path).read_bytes()
    b64 = base64.b64encode(img_bytes).decode("utf‑8")
    return f"data:image/png;base64,{b64}"