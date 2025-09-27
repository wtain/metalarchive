import json
import math

from storage_client.models import SessionLocal, PostMetric, engine
import pandas as pd


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


def coerce_int(value) -> int:
    if type(value) is float and math.isnan(value):
        return 0
    return int(value)


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


def load_posts_to_df():
    query = "SELECT post_id, timestamp, views, reactions, comments FROM posts_metrics"
    df = pd.read_sql(query, engine)
    return df
