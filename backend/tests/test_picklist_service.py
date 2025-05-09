# tests/test_picklist_service.py

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, MainItem
from app.services.picklist_service import generate_picklists

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # On doit alimenter last_import_date
    now = datetime.utcnow()
    session.add_all([
        MainItem(
            go_item="GO1-001",
            pick_status="NOT STARTED",
            redcon_status=1,
            item_number="001",
            part_number="P1",
            qty_req=5,
            last_import_date=now,
        ),
        MainItem(
            go_item="GO1-002",
            pick_status="NOT STARTED",
            redcon_status=1,
            item_number="002",
            part_number="P2",
            qty_req=3,
            last_import_date=now,
        ),
    ])
    session.commit()
    yield session
    session.close()

def test_generate_batch(db_session):
    picks = generate_picklists(db_session, mode="batch", qty_jobs=1)
    assert isinstance(picks, list) and len(picks) == 1
    pl = picks[0]
    assert pl["go_item"] == "GO1-001"
    assert len(pl["items"]) == 1
