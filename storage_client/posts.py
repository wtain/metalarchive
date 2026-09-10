import json
from collections import defaultdict

from storage_client.db_sync import SessionLocal, engine
# from storage_client.models import SessionLocal, PostMetric, engine, Subscriber
from storage_client.models import PostMetric, PostHeader, PostTags
import pandas as pd

from storage_client.utils import coerce_int


# Bulk-fetches title/tags for a set of post ids in 2 queries total, instead of
# the 2*N requests a per-post title/tags fetch would need for a list of posts.
def fetch_titles_and_tags(session, post_ids):
    if not post_ids:
        return {}

    titles = dict(
        session.query(PostHeader.post_id, PostHeader.title)
        .filter(PostHeader.post_id.in_(post_ids))
        .all()
    )

    tags_by_post = defaultdict(list)
    tag_rows = (
        session.query(PostTags.post_id, PostTags.id, PostTags.name, PostTags.probability)
        .filter(PostTags.post_id.in_(post_ids))
        .all()
    )
    for post_id, tag_id, name, probability in tag_rows:
        tags_by_post[post_id].append({"id": tag_id, "name": name, "probability": probability})

    return {
        post_id: {"title": titles.get(post_id), "tags": tags_by_post.get(post_id, [])}
        for post_id in post_ids
    }


def hydrate_posts(session, posts):
    details = fetch_titles_and_tags(session, [post["post_id"] for post in posts])
    for post in posts:
        info = details.get(post["post_id"], {"title": None, "tags": []})
        post["title"] = info["title"]
        post["tags"] = info["tags"]
    return posts


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
    if reactions == '':
        return 0
    data = json.loads(reactions)
    return sum(int(reaction['count']) for reaction in data["results"])


def save_posts_from_df(df: pd.DataFrame):
    session = SessionLocal()
    records = [
        PostMetric(
            post_id=row["message_id"],
            timestamp=pd.to_datetime(row["date"]),
            views=row["views"],
            reactions=
            count_reactions(row["reactions"]),
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
