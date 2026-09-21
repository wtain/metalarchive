
from collections import defaultdict

import pandas as pd
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import aliased

from storage_client.db_sync import SessionLocal, engine
# from storage_client.models import SessionLocal, Subscriber, engine, BatchRun
from storage_client.models import Subscriber, BatchRun
from storage_client.utils import coerce_string


# --- Add a single subscriber record ---
def add_subscriber(user_id, username=None, first_name=None, last_name=None, timestamp=None):
    session = SessionLocal()
    sub = Subscriber(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        timestamp=timestamp or datetime.utcnow(),
    )
    session.add(sub)
    session.commit()
    session.close()


# --- Save a whole DataFrame of subscribers snapshot ---
def save_subscribers_from_df(df: pd.DataFrame):
    session = SessionLocal()
    records = [
        Subscriber(
            user_id=row["user_id"],
            username=coerce_string(row.get("username")),
            first_name=coerce_string(row.get("first_name")),
            last_name=coerce_string(row.get("last_name")),
            timestamp=timestamp[0],
        )
        for timestamp, row in df.iterrows()
    ]
    session.add_all(records)
    session.commit()
    session.close()


# --- Load all subscribers into a DataFrame ---
def load_subscribers_to_df():
    query = "SELECT user_id, username, first_name, last_name, timestamp FROM subscribers"
    df = pd.read_sql(query, engine)
    return df


# select t.timestamp, count(*) from subscribers s,
# (select distinct timestamp from subscribers) t
# where s.timestamp=t.timestamp
# group by t.timestamp
# order by t.timestamp desc;
def subscribers_count_over_time(period, session):
    subscriber = aliased(Subscriber)
    batch_run = aliased(BatchRun)

    if period == "default" or period == "":
        q = (
            session.query(
                batch_run.timestamp,
                func.count(subscriber.id)
            )
            .join(subscriber, batch_run.id == subscriber.run_id)
            .group_by(batch_run.timestamp, batch_run.id)
            .order_by(batch_run.timestamp)
        )
    else:
        inner = (
            session.query(
                BatchRun.timestamp.label("timestamp"),
                func.count(Subscriber.id).label("subscribers_count"),
            )
            .join(
                Subscriber, BatchRun.id == Subscriber.run_id
            )
            .group_by(BatchRun.timestamp, BatchRun.id)
        ).subquery()

        format_period = {'daily': 'YYYY-MM-DD', 'weekly': 'YYYY-IW', 'monthly': 'YYYY-MM'}[period]
        group_by_expression = func.to_char(inner.c.timestamp, format_period).label("period")
        q = (
            session.query(
                group_by_expression,
                func.max(inner.c.subscribers_count).label("max_subscribers_count")
            )
            .group_by(group_by_expression)
            .order_by(group_by_expression)
        )

    return list(map(lambda record: { "timestamp": record[0], "count": record[1] }, q.all()))


# Walks every consecutive batch run in [start, end] and records each subscriber
# appearing/disappearing between two snapshots as a join/leave event, using the
# later run's timestamp as the (approximate, +-poll interval) event time. This
# catches churn (join and leave within the same period) that a start/end
# endpoint diff would miss.
def get_subscriber_changes(session, start, end):
    seed_run = (
        session.query(BatchRun.id)
        .filter(BatchRun.timestamp <= start)
        .order_by(BatchRun.timestamp.desc())
        .first()
    )

    runs_query = session.query(BatchRun.id, BatchRun.timestamp).filter(BatchRun.timestamp <= end)
    if seed_run is not None:
        runs_query = runs_query.filter(BatchRun.id >= seed_run.id)
    runs = runs_query.order_by(BatchRun.id).all()

    if len(runs) < 2:
        return {"new": [], "removed": []}

    run_ids = [run.id for run in runs]
    run_timestamp = {run.id: run.timestamp for run in runs}

    rows = (
        session.query(
            Subscriber.run_id,
            Subscriber.user_id,
            Subscriber.username,
            Subscriber.first_name,
            Subscriber.last_name,
        )
        .filter(Subscriber.run_id.in_(run_ids))
        .all()
    )

    by_run = defaultdict(dict)
    for run_id, user_id, username, first_name, last_name in rows:
        by_run[run_id][user_id] = (username, first_name, last_name)

    def to_event(user_id, details, timestamp):
        username, first_name, last_name = details
        return {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "timestamp": timestamp,
        }

    new_events = []
    removed_events = []
    previous_users = by_run.get(run_ids[0], {})

    for run_id in run_ids[1:]:
        current_users = by_run.get(run_id, {})
        timestamp = run_timestamp[run_id]

        for user_id in current_users.keys() - previous_users.keys():
            new_events.append(to_event(user_id, current_users[user_id], timestamp))

        for user_id in previous_users.keys() - current_users.keys():
            removed_events.append(to_event(user_id, previous_users[user_id], timestamp))

        previous_users = current_users

    new_events.sort(key=lambda e: e["timestamp"], reverse=True)
    removed_events.sort(key=lambda e: e["timestamp"], reverse=True)

    return {"new": new_events, "removed": removed_events}


# Reconstructs every subscribe/unsubscribe "stint" per user across the whole
# history, not just a period window - a user who joined, left, and rejoined
# gets one row per stint. Only ~100-ish users have ever subscribed, but the
# subscribers table re-snapshots everyone on every batch run (2M+ rows), so
# this fetches only the lean (run_id, user_id) presence pairs for the walk,
# then derives each user's single latest run_id from that in Python and
# fetches display details only for those specific runs - a `DISTINCT ON`
# ordered by (user_id, run_id) would need a full-table sort with no index
# to back it, since it also needs the non-indexed name columns.
def get_subscriber_lifecycles(session):
    runs = session.query(BatchRun.id, BatchRun.timestamp).order_by(BatchRun.id).all()
    if not runs:
        return {"past": [], "current": []}

    run_ids = [run.id for run in runs]
    run_timestamp = {run.id: run.timestamp for run in runs}

    # No run_id filter here: run_ids already spans every batch run that exists,
    # so filtering on it would just build a 20k+-value IN clause for no benefit.
    presence_rows = session.query(Subscriber.run_id, Subscriber.user_id).all()

    by_run = defaultdict(set)
    last_seen_run_id = {}
    for run_id, user_id in presence_rows:
        by_run[run_id].add(user_id)
        if run_id > last_seen_run_id.get(user_id, -1):
            last_seen_run_id[user_id] = run_id

    # Some batch runs recorded zero subscribers - a failed/incomplete Telegram
    # scrape (confirmed: an early period before subscriber tracking worked,
    # plus isolated later failures), not a real "everyone unsubscribed"
    # snapshot. Treating them as real would make the walk below see every
    # subscriber leave and immediately rejoin at the next real batch, wildly
    # inflating past-subscriber counts. Skip them as if never sampled.
    run_ids = [run_id for run_id in run_ids if by_run.get(run_id)]
    if not run_ids:
        return {"past": [], "current": []}
    latest_timestamp = run_timestamp[run_ids[-1]]

    desired_pairs = {(user_id, run_id) for user_id, run_id in last_seen_run_id.items()}
    latest_details = {}
    if desired_pairs:
        detail_rows = (
            session.query(Subscriber.user_id, Subscriber.run_id, Subscriber.username, Subscriber.first_name, Subscriber.last_name)
            .filter(Subscriber.run_id.in_(set(last_seen_run_id.values())))
            .all()
        )
        for user_id, run_id, username, first_name, last_name in detail_rows:
            if (user_id, run_id) in desired_pairs:
                latest_details[user_id] = {"username": username, "first_name": first_name, "last_name": last_name}

    def to_entry(user_id, added, removed):
        return {
            "user_id": user_id,
            **latest_details.get(user_id, {"username": None, "first_name": None, "last_name": None}),
            "added": added,
            "removed": removed,
            "duration_seconds": ((removed or latest_timestamp) - added).total_seconds(),
        }

    past = []
    open_stints = {}
    previous_users = set()

    for run_id in run_ids:
        current_users = by_run.get(run_id, set())
        timestamp = run_timestamp[run_id]

        for user_id in current_users - previous_users:
            open_stints[user_id] = timestamp

        for user_id in previous_users - current_users:
            added = open_stints.pop(user_id)
            past.append(to_entry(user_id, added, timestamp))

        previous_users = current_users

    current = [to_entry(user_id, added, None) for user_id, added in open_stints.items()]

    past.sort(key=lambda e: e["removed"], reverse=True)
    current.sort(key=lambda e: e["added"], reverse=True)

    return {"past": past, "current": current}
