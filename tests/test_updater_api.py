from datetime import datetime, timedelta

import pytest
from sqlalchemy import func

from storage_client.models import BatchRun, Post, PostEmbedding, Subscriber, SubscriberLifecycleStint

FAKE_EMBEDDING = [0.2] * 384


class FakeEmbeddingsExtractor:
    def get_embedding(self, text):
        return FAKE_EMBEDDING


@pytest.fixture(autouse=True)
def fake_embeddings_extractor(monkeypatch):
    monkeypatch.setattr("api.updater.EmbeddingsExtractor", FakeEmbeddingsExtractor)


def test_update_embeddings_computes_for_every_post_with_text(client, db_session):
    db_session.add_all([
        Post(id=1, text="Первый пост"),
        Post(id=2, text="Второй пост"),
        Post(id=3, text=None),
    ])
    db_session.commit()

    response = client.post("/api/updater/update_embeddings")
    assert response.status_code == 200

    embeddings = {e.post_id: e for e in db_session.query(PostEmbedding).all()}
    assert set(embeddings.keys()) == {1, 2}
    assert list(embeddings[1].embedding) == FAKE_EMBEDDING


def test_update_embeddings_recomputes_and_clears_stale_rows(client, db_session):
    db_session.add(Post(id=1, text="Первый пост"))
    db_session.add(PostEmbedding(post_id=1, model_name="old-model", embedding=[0.9] * 384))
    db_session.commit()

    response = client.post("/api/updater/update_embeddings")
    assert response.status_code == 200

    embeddings = db_session.query(PostEmbedding).filter(PostEmbedding.post_id == 1).all()
    assert len(embeddings) == 1
    assert list(embeddings[0].embedding) == FAKE_EMBEDDING


def _fake_poll_adding_batch(present_user_ids, timestamp):
    """Stands in for poll_from_telegram: records one more batch run in which
    exactly `present_user_ids` are subscribed."""
    async def fake_poll(db, channel_name):
        # Seed rows use explicit ids, which don't advance the id sequence.
        batch = BatchRun(id=db.query(func.max(BatchRun.id)).scalar() + 1, timestamp=timestamp)
        db.add(batch)
        db.flush()
        for user_id in present_user_ids:
            db.add(Subscriber(user_id=user_id, username=f"user{user_id}", run_id=batch.id))
        db.commit()
        return [len(present_user_ids), 0]
    return fake_poll


def test_update_records_subscriber_who_left_in_lifecycle_and_changes(client, db_session, monkeypatch):
    t0 = datetime(2026, 1, 1, 12, 0)
    db_session.add(BatchRun(id=1, timestamp=t0))
    db_session.add_all([
        Subscriber(user_id=1, username="stays", run_id=1),
        Subscriber(user_id=2, username="leaves", run_id=1),
    ])
    db_session.commit()

    t1 = t0 + timedelta(minutes=15)
    monkeypatch.setattr("api.updater.poll_from_telegram", _fake_poll_adding_batch({1}, t1))

    assert client.post("/api/updater/update").status_code == 200

    lifecycle = client.get("/api/subscribers/lifecycle").json()
    assert [(e["user_id"], e["removed"]) for e in lifecycle["past"]] == [(2, "2026-01-01T12:15:00")]
    assert [e["user_id"] for e in lifecycle["current"]] == [1]

    changes = db_session.query(SubscriberLifecycleStint).filter_by(user_id=2).one()
    assert changes.removed == t1


def test_update_refreshes_lifecycle_on_every_poll(client, db_session, monkeypatch):
    t0 = datetime(2026, 1, 1, 12, 0)
    db_session.add(BatchRun(id=1, timestamp=t0))
    db_session.add_all([
        Subscriber(user_id=1, run_id=1),
        Subscriber(user_id=2, run_id=1),
        Subscriber(user_id=3, run_id=1),
    ])
    db_session.commit()

    monkeypatch.setattr("api.updater.poll_from_telegram", _fake_poll_adding_batch({1, 2}, t0 + timedelta(minutes=15)))
    client.post("/api/updater/update")
    monkeypatch.setattr("api.updater.poll_from_telegram", _fake_poll_adding_batch({1}, t0 + timedelta(minutes=30)))
    client.post("/api/updater/update")

    past = client.get("/api/subscribers/lifecycle").json()["past"]
    assert sorted(e["user_id"] for e in past) == [2, 3]
