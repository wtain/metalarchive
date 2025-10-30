from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from daily_digest import get_last_run, get_subscribers_diffs, get_post_diffs
from db.session import get_db
from storage_client.models import Post, PostMetric, BatchRun

router = APIRouter()

# total views/reactions/comments per day
# top content
# extract post title and image
# single post views, reactions and comments over time


@router.get("/digest")
def get_digest(
    period: str = "daily",  # or "weekly", "monthly"
    db: Session = Depends(get_db)
):
    now = datetime.now()
    days = 1
    if period == "daily":
        days = 1
    elif period == "weekly":
        days = 7
    elif period == "monthly":
        days = 30
    # elif type(period) is int:
    else:
        days = int(period)
    reference = now - timedelta(days=days)
    latest_run_id = get_last_run(now)
    reference_run_id = get_last_run(reference)

    if not reference_run_id:
        return "No data"

    # todo: separate posts table + join + add post title
    diff = get_post_diffs(db, reference_run_id, latest_run_id)

    def convert_row(row):
        (post_text, post_id, views_old, views_new, views_diff, reactions_old, reactions_new, reactions_diff, comments_old,
         comments_new, comments_diff) = row
        return {"text": post_text, "post_id": post_id, "views_old": views_old, "views_new": views_new, "views_diff": views_diff,
                "reactions_old": reactions_old, "reactions_new": reactions_new, "reactions_diff": reactions_diff,
                "comments_old": comments_old,"comments_new": comments_new, "comments_diff": comments_diff}

    # todo: move conversion to the function itself
    posts_diff = list(filter(lambda r: r["views_diff"] > 0 or r["reactions_diff"] > 0 or r["comments_diff"] > 0,
                             map(convert_row, diff)))
    subscribers_diff = get_subscribers_diffs(db, reference_run_id, latest_run_id)

    return {
        "period": period,
        "subscribers": subscribers_diff,
        "posts": posts_diff
    }


@router.get("/top")
def get_top_posts(
    count: int = 10,
    db: Session = Depends(get_db)
):
    last_run_id = db.query(func.max(BatchRun.id)).one()[0]

    post = aliased(Post)
    post_metric = aliased(PostMetric)

    data = db.query(
        post.id,
        post.text,
        post_metric.views,
        post_metric.reactions,
        post_metric.comments,
    ).join(post_metric, post.id == post_metric.post_id
    ).filter(post_metric.run_id == last_run_id).order_by(post_metric.views.desc()).limit(count).all()

    return list(map(lambda row: { "post_id": row[0], "text": row[1], "views": row[2], "reactions": row[3], "comments": row[4] }, data))

