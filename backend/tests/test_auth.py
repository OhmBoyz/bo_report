import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models import Base
from app.database import get_db as original_get_db

# ------------------------------------------------------------------
# 1) Base SQLite "in-memory" *partagée* par StaticPool
# ------------------------------------------------------------------
engine = create_engine(
    "sqlite://",                                # mémoire partagée
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine)
transport = ASGITransport(app=app)

# ------------------------------------------------------------------
# 2) Fixture : reset des tables + override get_db()
# ------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _prepare_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[original_get_db] = override_get_db

# ------------------------------------------------------------------
# 3) Test end-to-end
# ------------------------------------------------------------------
@pytest.mark.asyncio
async def test_register_and_login_and_protected():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Enregistrement
        resp = await client.post("/auth/register", json={"username": "u1", "password": "pwd"})
        assert resp.status_code == 200

        # Auth (form-data + grant_type)
        resp = await client.post(
            "/auth/token",
            data={"grant_type": "password", "username": "u1", "password": "pwd"}
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]

        payload = {"mode": "batch", "qty_jobs": 1}

        # Sans token → 401
        resp = await client.post("/picklists/generate", json=payload)
        assert resp.status_code == 401

        # Avec token → 200
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post("/picklists/generate", headers=headers, json=payload)
        assert resp.status_code == 200
