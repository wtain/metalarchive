import os
import uuid

os.environ.setdefault("LOG_PATH", "/tmp/metalarchive-test-logs")
os.environ.setdefault("CORS_ALLOW_ORIGINS", "http://localhost")
# Must be set before any transformers/sentence-transformers/tokenizers import -
# the tokenizers Rust thread pool can deadlock under pytest otherwise.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
# Bounds the model-update-check network call so test runs can't hang on a
# flaky connection to huggingface.co - see the matching comment in backend.py.
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "3")

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
    # public stays in the search_path so extension-provided types (e.g. pgvector's
    # "vector", installed in public) resolve; app tables still go to the schema first.
    engine = create_engine(DATABASE_URL, connect_args={"options": f"-csearch_path={schema},public"})

    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {schema}"))
    # checkfirst=False: with public in the search_path (needed for pgvector's
    # "vector" type to resolve), the default checkfirst existence check finds
    # the real app tables already in public and wrongly skips creating fresh
    # ones in the test schema, so tests would silently hit production data.
    Base.metadata.create_all(engine, checkfirst=False)

    TestSessionLocal = sessionmaker(bind=engine)
    # Defensive: some legacy helpers (e.g. the dead daily_digest() script entry
    # point, storage_client/*'s older SessionLocal()-opening functions) still
    # open their own session via the module-level SessionLocal instead of
    # taking one as a parameter, bypassing the get_db() override below.
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
