
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
