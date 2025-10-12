from datetime import datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import aliased

from storage_client.models import SessionLocal, BatchRun, PostMetric


def get_last_run(day):
    session = SessionLocal()

    last_run = (
        session.query(
            BatchRun.id,
            BatchRun.timestamp,
        )
        .filter(
            BatchRun.timestamp <= day
        )
        .order_by(BatchRun.timestamp.desc())
        .first()
    )
    return last_run.id


def get_post_diffs(session, old_run_id, new_run_id):
    p1 = aliased(PostMetric)
    p2 = aliased(PostMetric)

    query = (
        session.query(
            func.coalesce(p1.post_id, p2.post_id).label("post_id"),
            p1.views.label("views_old"),
            p2.views.label("views_new"),
            (func.coalesce(p2.views, 0) - func.coalesce(p1.views, 0)).label("views_diff"),
            p1.reactions.label("reactions_old"),
            p2.reactions.label("reactions_new"),
            (func.coalesce(p2.reactions, 0) - func.coalesce(p1.reactions, 0)).label("reactions_diff"),
            p1.comments.label("comments_old"),
            p2.comments.label("comments_new"),
            (func.coalesce(p2.comments, 0) - func.coalesce(p1.comments, 0)).label("comments_diff"),
        )
        .outerjoin(p2, p1.post_id == p2.post_id)
        .filter(or_(p1.run_id == old_run_id, p1.run_id == None))   # left side
        .filter(or_(p2.run_id == new_run_id, p2.run_id == None))   # right side
    )

    query = query.filter(
        or_(
            (func.coalesce(p2.views, 0) - func.coalesce(p1.views, 0)) > 0,
            (func.coalesce(p2.reactions, 0) - func.coalesce(p1.reactions, 0)) > 0,
            (func.coalesce(p2.comments, 0) - func.coalesce(p1.comments, 0)) > 0
        )
    )

    return query.all()


"""
Дайджест за день, за неделю
- изменения в подписчиках
- изменения в постах
- изменения в лайках
- графики для топовых/последних постов (количества просмотров, реакций и комментариев) 
- число новых просмотров и реакций за период

Текущие значения подписок и просмотров
"""


def daily_digest():
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    latest_run_id = get_last_run(now)
    reference_run_id = get_last_run(yesterday)
    reference_run_id2 = get_last_run(week_ago)
    # print(reference_run_id, latest_run_id)
    session = SessionLocal()
    show_diff(latest_run_id, reference_run_id, session)
    show_diff(latest_run_id, reference_run_id2, session)


def show_diff(latest_run_id, reference_run_id, session):
    diff = get_post_diffs(session, reference_run_id, latest_run_id)
    # print(diff)
    for row in diff:
        post_id, views_old, views_new, views_diff, reactions_old, reactions_new, reactions_diff, comments_old, comments_new, comments_diff = row
        if views_diff == 0 and reactions_diff == 0 and comments_diff == 0:
            continue
        print(f"Post {post_id}")
        if views_diff > 0:
            print(f"- Views: {views_old} -> {views_new} (+{views_diff})")
        if reactions_diff > 0:
            print(f"- Reactions: {reactions_old} -> {reactions_new} (+{reactions_diff})")
        if comments_diff > 0:
            print(f"- Comments: {comments_old} -> {comments_new} (+{comments_diff})")
        print()

