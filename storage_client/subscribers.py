
import pandas as pd
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import aliased

from storage_client.models import SessionLocal, Subscriber, engine, BatchRun
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
