from datetime import datetime, timedelta

from storage_client.models import BatchRun, Subscriber
from storage_client.subscribers import get_subscriber_lifecycles


def make_run(db_session, run_id, timestamp):
    db_session.add(BatchRun(id=run_id, timestamp=timestamp))
    return timestamp


def add_presence(db_session, run_id, user_id, username="user", first_name="First", last_name="Last"):
    db_session.add(Subscriber(
        run_id=run_id, user_id=user_id, username=username, first_name=first_name, last_name=last_name,
    ))


def test_user_present_since_first_run_is_current_with_first_run_as_added(db_session):
    t0 = datetime(2026, 1, 1)
    t1 = t0 + timedelta(minutes=15)
    make_run(db_session, 1, t0)
    make_run(db_session, 2, t1)
    add_presence(db_session, 1, user_id=100)
    add_presence(db_session, 2, user_id=100)
    db_session.commit()

    result = get_subscriber_lifecycles(db_session)

    assert result["past"] == []
    assert len(result["current"]) == 1
    entry = result["current"][0]
    assert entry["user_id"] == 100
    assert entry["added"] == t0
    assert entry["removed"] is None
    assert entry["duration_seconds"] == (t1 - t0).total_seconds()


def test_user_who_left_appears_in_past_with_duration(db_session):
    t0 = datetime(2026, 1, 1)
    t1 = t0 + timedelta(minutes=15)
    t2 = t1 + timedelta(minutes=15)
    make_run(db_session, 1, t0)
    make_run(db_session, 2, t1)
    make_run(db_session, 3, t2)
    add_presence(db_session, 1, user_id=200)
    add_presence(db_session, 2, user_id=200)
    # absent from run 3 -> left, detected at t2
    db_session.commit()

    result = get_subscriber_lifecycles(db_session)

    assert result["current"] == []
    assert len(result["past"]) == 1
    entry = result["past"][0]
    assert entry["user_id"] == 200
    assert entry["added"] == t0
    assert entry["removed"] == t2
    assert entry["duration_seconds"] == (t2 - t0).total_seconds()


def test_rejoin_produces_two_separate_stints(db_session):
    timestamps = [datetime(2026, 1, 1) + timedelta(minutes=15 * i) for i in range(4)]
    for i, ts in enumerate(timestamps, start=1):
        make_run(db_session, i, ts)

    # present in run 1, absent in run 2 (left), present again in run 3 and 4 (rejoined, still current)
    add_presence(db_session, 1, user_id=300)
    add_presence(db_session, 3, user_id=300)
    add_presence(db_session, 4, user_id=300)
    db_session.commit()

    result = get_subscriber_lifecycles(db_session)

    assert len(result["past"]) == 1
    assert result["past"][0]["added"] == timestamps[0]
    assert result["past"][0]["removed"] == timestamps[1]

    assert len(result["current"]) == 1
    assert result["current"][0]["added"] == timestamps[2]
    assert result["current"][0]["removed"] is None


def test_lifecycle_endpoint_returns_hydrated_entries(client, db_session):
    t0 = datetime(2026, 1, 1)
    make_run(db_session, 1, t0)
    add_presence(db_session, 1, user_id=400, username="alice", first_name="Alice", last_name="A")
    db_session.commit()

    response = client.get("/api/subscribers/lifecycle")
    assert response.status_code == 200

    data = response.json()
    assert data["past"] == []
    assert len(data["current"]) == 1
    assert data["current"][0]["username"] == "alice"
    assert data["current"][0]["removed"] is None
