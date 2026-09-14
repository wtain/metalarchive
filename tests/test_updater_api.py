import pytest

from storage_client.models import Post, PostEmbedding

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
