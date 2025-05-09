from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Charge le bon .env (ici .env.dev en dev local)
load_dotenv('.env.dev')
DATABASE_URL = os.getenv('DATABASE_URL')     # ← ou '.env' / '.env.prod' selon l'environnement

# Si vous utilisez SQLite en dev, il faut ce paramètre
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Création de l'engine
engine = create_engine(DATABASE_URL)
# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Cette fonction sera utilisée par FastAPI comme dépendance
def get_db() -> Generator[Session, None, None]:
    """
    Ouvre une session DB, la yield à FastAPI, et la ferme une fois la requête terminée.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()