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
    # absent from run 3 -> left, detected at t2; decoy keeps run 3 non-empty
    # so it isn't treated as a failed-scrape batch and skipped.
    add_presence(db_session, 3, user_id=999)
    db_session.commit()

    result = get_subscriber_lifecycles(db_session)

    assert [e["user_id"] for e in result["current"]] == [999]
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
    # run 2 has a decoy subscriber so it's a real (non-empty) batch, not the
    # zero-subscriber-batch case covered separately below.
    add_presence(db_session, 1, user_id=300)
    add_presence(db_session, 2, user_id=999)
    add_presence(db_session, 3, user_id=300)
    add_presence(db_session, 4, user_id=300)
    db_session.commit()

    result = get_subscriber_lifecycles(db_session)
    past_300 = [e for e in result["past"] if e["user_id"] == 300]
    current_300 = [e for e in result["current"] if e["user_id"] == 300]

    assert len(past_300) == 1
    assert past_300[0]["added"] == timestamps[0]
    assert past_300[0]["removed"] == timestamps[1]

    assert len(current_300) == 1
    assert current_300[0]["added"] == timestamps[2]
    assert current_300[0]["removed"] is None


def test_zero_subscriber_batch_is_skipped_not_treated_as_mass_unsubscribe(db_session):
    # Regression test: a batch run with zero subscriber rows is a failed/
    # incomplete scrape, not a real "everyone unsubscribed" snapshot. It must
    # not be read as every subscriber leaving and immediately rejoining.
    timestamps = [datetime(2026, 1, 1) + timedelta(minutes=15 * i) for i in range(3)]
    for i, ts in enumerate(timestamps, start=1):
        make_run(db_session, i, ts)

    add_presence(db_session, 1, user_id=500)
    # run 2: no subscriber rows at all (the failure mode)
    add_presence(db_session, 3, user_id=500)
    db_session.commit()

    result = get_subscriber_lifecycles(db_session)

    assert result["past"] == []
    assert len(result["current"]) == 1
    assert result["current"][0]["user_id"] == 500
    assert result["current"][0]["added"] == timestamps[0]


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
