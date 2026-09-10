import os
import uuid

os.environ.setdefault("LOG_PATH", "/tmp/metalarchive-test-logs")
os.environ.setdefault("CORS_ALLOW_ORIGINS", "http://localhost")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from db.session import get_db
from storage_client.models import Base

DATABASE_URL = os.environ.get("SYNC_DATABASE_URL")


@pytest.fixture(scope="session", autouse=True)
def _require_test_database():
    if not DATABASE_URL:
        pytest.skip("SYNC_DATABASE_URL is not set; tests need a reachable Postgres (see docs/environments.md)")
    try:
        create_engine(DATABASE_URL).connect().close()
    except Exception as exc:
        pytest.skip(f"Postgres not reachable at SYNC_DATABASE_URL ({exc}); run `docker-compose up -d db`")


# Tests run against a real Postgres (not SQLite) because the app relies on
# Postgres-only SQL (DISTINCT ON, to_char) that SQLite can't execute. Each test
# gets its own throwaway schema so it never touches real app data.
@pytest.fixture()
def db_session(monkeypatch):
    schema = f"test_{uuid.uuid4().hex[:8]}"
    engine = create_engine(DATABASE_URL, connect_args={"options": f"-csearch_path={schema}"})

    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {schema}"))
    Base.metadata.create_all(engine)

    TestSessionLocal = sessionmaker(bind=engine)
    # get_last_run() in daily_digest.py opens its own session via the module-level
    # SessionLocal instead of taking one as a parameter, so it has to be patched
    # separately from the get_db() override below to actually hit the test schema.
    monkeypatch.setattr("daily_digest.SessionLocal", TestSessionLocal)
    monkeypatch.setattr("storage_client.db_sync.SessionLocal", TestSessionLocal)

    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        with engine.begin() as conn:
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        engine.dispose()


@pytest.fixture()
def client(db_session):
    from backend import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
