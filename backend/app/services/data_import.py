# backend/app/services/data_import.py
import pandas as pd
from fastapi import HTTPException
from .utils import _find_column

def read_redcon_df(file_path: str) -> pd.DataFrame:
    """Lit la feuille REDCON (Export) depuis un fichier Excel."""
    try:
        df = pd.read_excel(file_path, sheet_name='Export')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lecture Excel REDCON: {e}")
    return df

def read_backlog_df(file_path: str) -> pd.DataFrame:
    """Lit la feuille Backlog (Sheet1) depuis un fichier Excel."""
    try:
        df = pd.read_excel(file_path, sheet_name='Sheet1')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lecture Excel Backlog: {e}")
    return df
