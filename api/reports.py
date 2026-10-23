import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from daily_digest import get_last_run, get_subscribers_diffs, get_post_diffs
from db.session import get_db
from storage_client.models import Post, PostMetric, BatchRun, Subscriber
from storage_client.posts import hydrate_posts
from storage_client.subscribers import get_subscriber_changes


logger = logging.getLogger("uvicorn.info")

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
    elif period != "default":
        days = int(period)
    if days:
        reference = now - timedelta(days=days)
    latest_run_id = get_last_run(db, now)
    if period == "default":
        reference_run_id = (
            db.query(
                func.max(BatchRun.id)
            )
            .filter(BatchRun.id < latest_run_id)
        ).one()[0]
    else:
        reference_run_id = get_last_run(db, reference)

    if not reference_run_id:
        return "No data"

    logger.info(f"Reference run id: {reference_run_id}")

    # todo: separate posts table + join + add post title
    diff = get_post_diffs(db, reference_run_id, latest_run_id)

    def convert_row(row):
        (post_text, post_id, views_old, views_new, views_diff, reactions_old, reactions_new, reactions_diff, comments_old,
         comments_new, comments_diff, is_new) = row
        return {"text": post_text, "post_id": post_id, "views_old": views_old, "views_new": views_new, "views_diff": views_diff,
                "reactions_old": reactions_old, "reactions_new": reactions_new, "reactions_diff": reactions_diff,
                "comments_old": comments_old,"comments_new": comments_new, "comments_diff": comments_diff, "is_new": is_new}

    # todo: move conversion to the function itself
    posts_diff = hydrate_posts(db, list(map(convert_row, diff)))
    subscribers_diff = get_subscribers_diffs(db, reference_run_id, latest_run_id)

    views_total = sum(map(lambda diff: diff["views_diff"], posts_diff))
    reactions_total = sum(map(lambda diff: diff["reactions_diff"], posts_diff))
    comments_total = sum(map(lambda diff: diff["comments_diff"], posts_diff))

    return {
        "period": period,
        "subscribers": subscribers_diff,
        "posts": posts_diff,
        "views_total": views_total,
        "reactions_total": reactions_total,
        "comments_total": comments_total,
    }


def _as_utc(timestamp: datetime) -> datetime:
    # BatchRun.timestamp is naive UTC (datetime.utcnow); serialize it with an
    # explicit offset so browsers don't parse it as local time.
    return timestamp.replace(tzinfo=timezone.utc)


@router.get("/freshness")
def get_freshness(db: Session = Depends(get_db)):
    latest = db.query(func.max(BatchRun.timestamp)).scalar()
    return {"as_of": _as_utc(latest) if latest else None}


PERIOD_TO_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}


def _metric_totals(db: Session, run_id: int) -> dict:
    views, reactions, comments = db.query(
        func.coalesce(func.sum(PostMetric.views), 0),
        func.coalesce(func.sum(PostMetric.reactions), 0),
        func.coalesce(func.sum(PostMetric.comments), 0),
    ).filter(PostMetric.run_id == run_id).one()
    return {"views": int(views), "reactions": int(reactions), "comments": int(comments)}


@router.get("/summary")
def get_summary(
    period: str = "daily",  # or "default" (since previous batch run), "weekly", "monthly"
    db: Session = Depends(get_db)
):
    """Consolidated report: current totals plus what changed over the period."""
    latest = db.query(BatchRun).order_by(BatchRun.id.desc()).first()
    if latest is None:
        return {"period": period, "available": False}

    if period == "default":
        reference = (
            db.query(BatchRun)
            .filter(BatchRun.id < latest.id)
            .order_by(BatchRun.id.desc())
            .first()
        )
    else:
        # Anchored on the latest run rather than wall-clock "now", so a stale
        # scraper still yields a report for the window ending at its last data.
        reference = (
            db.query(BatchRun)
            .filter(BatchRun.timestamp <= latest.timestamp - timedelta(days=PERIOD_TO_DAYS.get(period, 1)))
            .order_by(BatchRun.timestamp.desc())
            .first()
        )
    if reference is None:
        return {"period": period, "available": False}

    totals_now = _metric_totals(db, latest.id)
    totals_before = _metric_totals(db, reference.id)

    subscribers_now = db.query(func.count(Subscriber.id)).filter(Subscriber.run_id == latest.id).scalar()
    subscribers_before = db.query(func.count(Subscriber.id)).filter(Subscriber.run_id == reference.id).scalar()
    changes = get_subscriber_changes(db, reference.timestamp, latest.timestamp)

    new_posts = [
        {"post_id": row[1], "text": row[0], "views": row[3], "reactions": row[6], "comments": row[9]}
        for row in get_post_diffs(db, reference.id, latest.id)
        if row[11] and row[3] is not None  # is_new and has metrics in the latest run
    ]

    return {
        "period": period,
        "available": True,
        "from": _as_utc(reference.timestamp),
        "to": _as_utc(latest.timestamp),
        "posts": {
            "total": db.query(func.count(Post.id)).scalar(),
            "new_count": len(new_posts),
            "new": hydrate_posts(db, new_posts),
        },
        "subscribers": {
            "total": subscribers_now,
            "change": subscribers_now - subscribers_before,
            "new_count": len(changes["new"]),
            "removed_count": len(changes["removed"]),
            "new": changes["new"],
            "removed": changes["removed"],
        },
        "views": {"total": totals_now["views"], "change": totals_now["views"] - totals_before["views"]},
        "reactions": {"total": totals_now["reactions"], "change": totals_now["reactions"] - totals_before["reactions"]},
        "comments": {"total": totals_now["comments"], "change": totals_now["comments"] - totals_before["comments"]},
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

    posts = list(map(lambda row: { "post_id": row[0], "text": row[1], "views": row[2], "reactions": row[3], "comments": row[4] }, data))
    return hydrate_posts(db, posts)

