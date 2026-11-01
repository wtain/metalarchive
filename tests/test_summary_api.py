from datetime import datetime, timedelta

from storage_client.models import BatchRun, Post, PostMetric, Subscriber


def _seed(db_session):
    now = datetime.utcnow()
    db_session.add_all([
        BatchRun(id=1, timestamp=now - timedelta(days=2)),
        BatchRun(id=2, timestamp=now),
    ])
    db_session.add_all([Post(id=1, text="Old"), Post(id=2, text="New")])
    db_session.add_all([
        PostMetric(post_id=1, run_id=1, views=10, reactions=1, comments=0),
        PostMetric(post_id=1, run_id=2, views=25, reactions=3, comments=2),
        PostMetric(post_id=2, run_id=2, views=7, reactions=0, comments=0),
    ])
    db_session.add_all([
        Subscriber(user_id=100, run_id=1, first_name="Stays"),
        Subscriber(user_id=101, run_id=1, first_name="Leaves"),
        Subscriber(user_id=100, run_id=2, first_name="Stays"),
        Subscriber(user_id=102, run_id=2, first_name="Joins"),
        Subscriber(user_id=103, run_id=2, first_name="AlsoJoins"),
    ])
    db_session.commit()


def test_summary_totals_and_changes(client, db_session):
    _seed(db_session)

    data = client.get("/api/reports/summary?period=daily").json()

    assert data["available"] is True
    assert data["posts"]["total"] == 2
    assert data["posts"]["new_count"] == 1
    assert data["posts"]["new"][0]["post_id"] == 2
    assert data["subscribers"]["total"] == 3
    assert data["subscribers"]["change"] == 1
    assert data["subscribers"]["new_count"] == 2
    assert data["subscribers"]["removed_count"] == 1
    assert data["views"] == {"total": 32, "change": 22}
    assert data["reactions"] == {"total": 3, "change": 2}
    assert data["comments"] == {"total": 2, "change": 2}


def test_summary_new_posts_include_published_at(client, db_session):
    _seed(db_session)
    published = datetime(2026, 1, 1, 9, 30, 0)
    for metric in db_session.query(PostMetric).filter(PostMetric.post_id == 2):
        metric.timestamp = published
    db_session.commit()

    new_post = client.get("/api/reports/summary?period=daily").json()["posts"]["new"][0]

    assert new_post["published_at"] == "2026-01-01T09:30:00+00:00"


def test_summary_default_period_uses_previous_run(client, db_session):
    _seed(db_session)
    data = client.get("/api/reports/summary?period=default").json()
    assert data["available"] is True
    assert data["views"]["change"] == 22


def test_summary_without_reference_run_is_unavailable(client, db_session):
    db_session.add(BatchRun(id=1, timestamp=datetime.utcnow()))
    db_session.commit()
    assert client.get("/api/reports/summary?period=weekly").json()["available"] is False


def test_freshness_returns_latest_run_as_utc(client, db_session):
    db_session.add_all([
        BatchRun(id=1, timestamp=datetime(2026, 1, 1, 10, 0, 0)),
        BatchRun(id=2, timestamp=datetime(2026, 1, 1, 10, 15, 0)),
    ])
    db_session.commit()
    assert client.get("/api/reports/freshness").json() == {"as_of": "2026-01-01T10:15:00+00:00"}


def test_freshness_without_runs(client, db_session):
    assert client.get("/api/reports/freshness").json() == {"as_of": None}
