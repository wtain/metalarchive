from datetime import datetime, timedelta

from storage_client.models import BatchRun, Post, PostHeader, PostMetric


def test_top_posts_are_hydrated_with_title_and_tags(client, db_session):
    db_session.add(BatchRun(id=1, timestamp=datetime.utcnow()))
    db_session.add(Post(id=1, text="Hello"))
    db_session.add(PostHeader(post_id=1, title="Hello Title"))
    db_session.add(PostMetric(post_id=1, run_id=1, views=100, reactions=5, comments=2))
    db_session.commit()

    response = client.get("/api/reports/top?count=5")
    assert response.status_code == 200

    posts = response.json()
    assert len(posts) == 1
    assert posts[0]["title"] == "Hello Title"
    assert posts[0]["tags"] == []
    assert posts[0]["views"] == 100


def test_digest_flags_new_post_and_hydrates_it(client, db_session):
    now = datetime.utcnow()
    old_run = BatchRun(id=1, timestamp=now - timedelta(days=2))
    new_run = BatchRun(id=2, timestamp=now)
    db_session.add_all([old_run, new_run])
    db_session.add(Post(id=1, text="Brand new post"))
    db_session.add(PostHeader(post_id=1, title="Brand New"))
    db_session.add(PostMetric(post_id=1, run_id=2, views=5, reactions=0, comments=0))
    db_session.commit()

    response = client.get("/api/reports/digest?period=daily")
    assert response.status_code == 200

    data = response.json()
    posts = data["posts"]
    assert len(posts) == 1
    assert posts[0]["is_new"] is True
    assert posts[0]["title"] == "Brand New"
    assert posts[0]["views_old"] is None
    assert posts[0]["views_new"] == 5


def test_digest_excludes_post_with_no_change(client, db_session):
    now = datetime.utcnow()
    old_run = BatchRun(id=1, timestamp=now - timedelta(days=2))
    new_run = BatchRun(id=2, timestamp=now)
    db_session.add_all([old_run, new_run])
    db_session.add(Post(id=1, text="Unchanged post"))
    db_session.add(PostMetric(post_id=1, run_id=1, views=5, reactions=0, comments=0))
    db_session.add(PostMetric(post_id=1, run_id=2, views=5, reactions=0, comments=0))
    db_session.commit()

    response = client.get("/api/reports/digest?period=daily")
    assert response.status_code == 200
    assert response.json()["posts"] == []
