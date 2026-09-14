import pytest

from database_saver.posts import PostsStatsDatabaseSaver
from storage_client.models import BatchRun, Post, PostEmbedding, PostHeader, PostMetric

FAKE_EMBEDDING = [0.1] * 384


class FakeTagsExtractor:
    def get_tags(self, text):
        return [("tag", 0.5)]


class FakeTitleExtractor:
    def get_title(self, text):
        return "Fake Title"


class FakeEmbeddingsExtractor:
    def get_embedding(self, text):
        return FAKE_EMBEDDING


@pytest.fixture(autouse=True)
def fake_ai_extractors(monkeypatch):
    # Avoid loading real KeyBERT/rut5/sentence-transformers models (slow, heavy downloads) in tests.
    monkeypatch.setattr("database_saver.posts.TagsExtractor", FakeTagsExtractor)
    monkeypatch.setattr("database_saver.posts.TitleExtractor", FakeTitleExtractor)
    monkeypatch.setattr("database_saver.posts.EmbeddingsExtractor", FakeEmbeddingsExtractor)


def make_batch(db_session):
    batch = BatchRun()
    db_session.add(batch)
    db_session.flush()
    return batch


def test_new_post_and_metric_save_without_fk_violation(db_session):
    batch = make_batch(db_session)

    with PostsStatsDatabaseSaver(db_session, batch.id) as saver:
        saver.write_row(id=1, date=batch.timestamp, views=10, forwards=0, reactions="", comments=2, text="Brand new post")
    db_session.commit()

    post = db_session.query(Post).filter(Post.id == 1).one()
    metric = db_session.query(PostMetric).filter(PostMetric.post_id == 1).one()
    header = db_session.query(PostHeader).filter(PostHeader.post_id == 1).one()
    embedding = db_session.query(PostEmbedding).filter(PostEmbedding.post_id == 1).one()

    assert post.text == "Brand new post"
    assert metric.views == 10
    assert metric.run_id == batch.id
    assert header.title == "Fake Title"
    assert list(embedding.embedding) == FAKE_EMBEDDING


def test_existing_post_text_update_does_not_touch_header(db_session):
    batch = make_batch(db_session)
    db_session.add(Post(id=1, text="Old text"))
    db_session.add(PostHeader(post_id=1, title="Original Title"))
    db_session.commit()

    with PostsStatsDatabaseSaver(db_session, batch.id) as saver:
        saver.write_row(id=1, date=batch.timestamp, views=5, forwards=0, reactions="", comments=0, text="Edited text")
    db_session.commit()

    post = db_session.query(Post).filter(Post.id == 1).one()
    header = db_session.query(PostHeader).filter(PostHeader.post_id == 1).one()

    assert post.text == "Edited text"
    assert header.title == "Original Title"


def test_new_and_existing_posts_in_the_same_batch(db_session):
    batch = make_batch(db_session)
    db_session.add(Post(id=1, text="Existing post"))
    db_session.commit()

    with PostsStatsDatabaseSaver(db_session, batch.id) as saver:
        saver.write_row(id=1, date=batch.timestamp, views=1, forwards=0, reactions="", comments=0, text="Existing post")
        saver.write_row(id=2, date=batch.timestamp, views=2, forwards=0, reactions="", comments=0, text="New post")
    db_session.commit()

    metrics = {m.post_id: m for m in db_session.query(PostMetric).all()}
    assert metrics[1].views == 1
    assert metrics[2].views == 2
    assert db_session.query(Post).filter(Post.id == 2).one().text == "New post"
