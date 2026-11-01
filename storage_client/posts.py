import json
from collections import defaultdict
from datetime import timezone

from sqlalchemy import func

from environment.media import MEDIA_URL_PREFIX
from storage_client.db_sync import SessionLocal, engine
# from storage_client.models import SessionLocal, PostMetric, engine, Subscriber
from storage_client.models import PostMetric, PostHeader, PostTags, PostImage
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


def fetch_images(session, post_ids):
    if not post_ids:
        return {}

    images_by_post = defaultdict(list)
    image_rows = (
        session.query(PostImage.post_id, PostImage.id, PostImage.file_name)
        .filter(PostImage.post_id.in_(post_ids))
        .order_by(PostImage.position)
        .all()
    )
    for post_id, image_id, file_name in image_rows:
        images_by_post[post_id].append({"id": image_id, "url": f"{MEDIA_URL_PREFIX}/{file_name}"})

    return images_by_post


# PostMetric.timestamp is the Telegram message date (naive UTC), repeated on
# every batch's row, so the earliest one is the publication time. Post.created_at
# is only when we first scraped the post.
def fetch_published_at(session, post_ids):
    if not post_ids:
        return {}
    rows = (
        session.query(PostMetric.post_id, func.min(PostMetric.timestamp))
        .filter(PostMetric.post_id.in_(post_ids))
        .group_by(PostMetric.post_id)
        .all()
    )
    return {
        post_id: timestamp.replace(tzinfo=timezone.utc) if timestamp else None
        for post_id, timestamp in rows
    }


def hydrate_posts(session, posts):
    post_ids = [post["post_id"] for post in posts]
    published_at = fetch_published_at(session, post_ids)
    details = fetch_titles_and_tags(session, post_ids)
    images_by_post = fetch_images(session, post_ids)
    for post in posts:
        info = details.get(post["post_id"], {"title": None, "tags": []})
        post["title"] = info["title"]
        post["tags"] = info["tags"]
        post["images"] = images_by_post.get(post["post_id"], [])
        post["published_at"] = published_at.get(post["post_id"])
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
