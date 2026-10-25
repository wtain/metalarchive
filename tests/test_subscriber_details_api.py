import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace

from storage_client.models import BatchRun, Subscriber, SubscriberLifecycleStint, SubscriberPhoto
from storage_client.subscribers import update_subscriber_lifecycle
from synchronizer.poller import pick_subscriber_photos_to_download, sync_subscriber_photos

T0 = datetime(2026, 1, 1, 12, 0)


def seed_history(db_session):
    """user 1: present runs 1-2, absent run 3, back in run 4 (renamed).
    user 2: present throughout. Run 3 has user 2 so it isn't a failed scrape."""
    for run_id in range(1, 5):
        db_session.add(BatchRun(id=run_id, timestamp=T0 + timedelta(minutes=15 * (run_id - 1))))
    for run_id in (1, 2):
        db_session.add(Subscriber(user_id=1, run_id=run_id, username="old", first_name="Old"))
    db_session.add(Subscriber(user_id=1, run_id=4, username="new", first_name="New"))
    for run_id in range(1, 5):
        db_session.add(Subscriber(user_id=2, run_id=run_id, username="other"))
    db_session.commit()
    update_subscriber_lifecycle(db_session)


def test_details_summarizes_stints_and_name_history(client, db_session):
    seed_history(db_session)

    data = client.get("/api/subscribers/1").json()

    assert data["user_id"] == 1
    assert data["status"] == "subscribed"
    assert data["username"] == "new"
    assert data["first_seen"] == "2026-01-01T12:00:00"
    assert data["last_seen"] == "2026-01-01T12:45:00"
    assert data["subscribed_since"] == "2026-01-01T12:45:00"
    assert data["stints_count"] == 2
    assert data["rejoin_count"] == 1
    # stint 1: 12:00 -> 12:30 (left, detected at run 3) ; stint 2: 12:45 -> latest run (0s)
    assert data["total_subscribed_seconds"] == 30 * 60
    assert [s["removed"] for s in data["stints"]] == [None, "2026-01-01T12:30:00"]
    assert [n["username"] for n in data["name_history"]] == ["new", "old"]


def test_details_for_subscriber_who_left(client, db_session):
    seed_history(db_session)
    db_session.add(BatchRun(id=5, timestamp=T0 + timedelta(minutes=60)))
    db_session.add(Subscriber(user_id=2, run_id=5, username="other"))
    db_session.commit()
    update_subscriber_lifecycle(db_session)

    data = client.get("/api/subscribers/1").json()

    assert data["status"] == "left"
    assert data["left_at"] == "2026-01-01T13:00:00"
    assert data["subscribed_since"] is None


def test_details_unknown_subscriber_is_404(client, db_session):
    assert client.get("/api/subscribers/999").status_code == 404


def test_literal_subscriber_routes_still_resolve(client, db_session):
    seed_history(db_session)
    assert client.get("/api/subscribers/lifecycle").status_code == 200
    assert client.get("/api/subscribers/changes?period=weekly").status_code == 200


def test_photo_url_is_attached_to_details_changes_and_lifecycle(client, db_session):
    seed_history(db_session)
    db_session.add(SubscriberPhoto(user_id=1, photo_id=77, file_name="subscriber_1_77.jpg"))
    db_session.commit()

    assert client.get("/api/subscribers/1").json()["photo_url"] == "/media/subscriber_1_77.jpg"
    assert client.get("/api/subscribers/2").json()["photo_url"] is None

    lifecycle = client.get("/api/subscribers/lifecycle").json()
    urls = {e["user_id"]: e["photo_url"] for e in lifecycle["past"] + lifecycle["current"]}
    assert urls == {1: "/media/subscriber_1_77.jpg", 2: None}

    changes = client.get("/api/subscribers/changes?period=weekly").json()
    for event in changes["new"] + changes["removed"]:
        assert "photo_url" in event


def user(user_id, photo_id=None):
    return SimpleNamespace(id=user_id, photo=SimpleNamespace(photo_id=photo_id) if photo_id else None)


def test_pick_skips_users_without_photo_and_with_up_to_date_photo():
    users = [user(1), user(2, photo_id=20), user(3, photo_id=30), user(4, photo_id=41)]

    picked = pick_subscriber_photos_to_download(users, known_photo_ids={3: 30, 4: 40}, limit=10)

    assert [(u.id, photo_id) for u, photo_id in picked] == [(2, 20), (4, 41)]


def test_pick_respects_limit():
    users = [user(i, photo_id=i) for i in range(1, 11)]
    assert len(pick_subscriber_photos_to_download(users, {}, limit=3)) == 3


class FakePhotoClient:
    def __init__(self, failing_user_ids=()):
        self.failing_user_ids = set(failing_user_ids)
        self.calls = []

    async def download_profile_photo(self, user, dest_dir, file_name):
        self.calls.append(file_name)
        return None if user.id in self.failing_user_ids else file_name


def test_sync_stores_photos_replaces_changed_ones_and_skips_failures(db_session):
    db_session.add(SubscriberPhoto(user_id=1, photo_id=10, file_name="subscriber_1_10.jpg"))
    db_session.commit()
    users = [user(1, photo_id=11), user(2, photo_id=20), user(3, photo_id=30)]
    telegram = FakePhotoClient(failing_user_ids=[3])

    downloaded = asyncio.run(sync_subscriber_photos(telegram, db_session, users))
    db_session.commit()

    assert downloaded == 2
    rows = {p.user_id: (p.photo_id, p.file_name) for p in db_session.query(SubscriberPhoto).all()}
    assert rows == {1: (11, "subscriber_1_11.jpg"), 2: (20, "subscriber_2_20.jpg")}
