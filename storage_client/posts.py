import json

from sqlalchemy import distinct, select, func

from storage_client.models import SessionLocal, PostMetric, engine, Subscriber
import pandas as pd

from storage_client.utils import coerce_int


def add_post_metric(post_id, views, reactions, comments):
    session = SessionLocal()
    metric = PostMetric(
        post_id=post_id,
        views=views,
        reactions=reactions,
        comments=comments,
    )
    session.add(metric)
    session.commit()
    session.close()


def count_reactions(reactions) -> int:
    if type(reactions) is not str:
        return 0
    data = json.loads(reactions)
    return int(data["results"][0]['count'])


def save_posts_from_df(df: pd.DataFrame):
    session = SessionLocal()
    records = [
        PostMetric(
            post_id=row["message_id"],
            timestamp=pd.to_datetime(row["date"]),
            views=row["views"],
            reactions=count_reactions(row["reactions"]),
            comments=coerce_int(row["comments"]),
        )
        for _, row in df.iterrows()
    ]
    session.add_all(records)
    session.commit()
    session.close()


# select t.timestamp, count(*) from subscribers s,
# (select distinct timestamp from subscribers) t
# where s.timestamp=t.timestamp
# group by t.timestamp
# order by t.timestamp desc;
def subscribers_count_over_time():
    session = SessionLocal()

    q = (
        session.query(
            Subscriber.timestamp,
            func.count(Subscriber.id)
        )
        .group_by(Subscriber.timestamp)
        .order_by(Subscriber.timestamp)
    )
    return q.all()


def load_posts_to_df():
    query = "SELECT post_id, timestamp, views, reactions, comments FROM posts_metrics"
    df = pd.read_sql(query, engine)
    return df
