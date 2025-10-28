from datetime import datetime, timedelta
from operator import and_

from sqlalchemy import func, or_
from sqlalchemy.orm import aliased

from storage_client.models import SessionLocal, BatchRun, PostMetric, Subscriber, Post


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
    return last_run.id if last_run else None


def get_post_diffs(session, old_run_id, new_run_id):
    p1 = aliased(PostMetric)
    p2 = aliased(PostMetric)

    query = (
        session.query(
            Post.text,
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
        .join(Post, Post.id == p2.post_id)
        .filter(or_(p1.run_id == old_run_id, p1.run_id is None))   # left side
        .filter(or_(p2.run_id == new_run_id, p2.run_id is None))   # right side
    )

    query = query.filter(
        or_(
            (func.coalesce(p2.views, 0) - func.coalesce(p1.views, 0)) > 0,
            (func.coalesce(p2.reactions, 0) - func.coalesce(p1.reactions, 0)) > 0,
            (func.coalesce(p2.comments, 0) - func.coalesce(p1.comments, 0)) > 0
        )
    )

    return query.all()


def get_subscribers_diffs(session, old_run_id, new_run_id):
    p1 = aliased(Subscriber)
    p2 = aliased(Subscriber)

    query_removed = (
        session.query(
            func.coalesce(p1.user_id, p2.user_id).label("user_id"),
            p1.user_id.label("user_id_old"),
            p2.user_id.label("user_id_new"),
            p1.first_name,
            p2.first_name,
        )
        .outerjoin(p2, and_(
                p1.user_id == p2.user_id,
                or_(p2.run_id == new_run_id, p2.run_id is None)
            ),
            full=True)
        # .filter(
        #     or_(
        #         or_(p1.run_id == old_run_id, p1.run_id is None),
        #         or_(p2.run_id == new_run_id, p2.run_id is None)
        #     )
        # )
        .filter(or_(p1.run_id == old_run_id, p1.run_id is None))   # left side
        # .filter(or_(p2.run_id == new_run_id, p2.run_id is None))   # right side
    )

    query_added = (
        session.query(
            func.coalesce(p1.user_id, p2.user_id).label("user_id"),
            p1.user_id.label("user_id_old"),
            p2.user_id.label("user_id_new"),
            p1.first_name,
            p2.first_name,
        )
        .outerjoin(p2, and_(
            p1.user_id == p2.user_id,
            or_(p2.run_id == old_run_id, p2.run_id is None)
        ),
                   full=True)
        # .filter(
        #     or_(
        #         or_(p1.run_id == old_run_id, p1.run_id is None),
        #         or_(p2.run_id == new_run_id, p2.run_id is None)
        #     )
        # )
        .filter(or_(p1.run_id == new_run_id, p1.run_id is None))  # left side
        # .filter(or_(p2.run_id == new_run_id, p2.run_id is None))   # right side
    )

    added = query_added.filter(p2.user_id.is_(None)).all()
    removed = query_removed.filter(p2.user_id.is_(None)).all()

    # query = query.filter(
    #     or_(
    #         (func.coalesce(p2.views, 0) - func.coalesce(p1.views, 0)) > 0,
    #         (func.coalesce(p2.reactions, 0) - func.coalesce(p1.reactions, 0)) > 0,
    #         (func.coalesce(p2.comments, 0) - func.coalesce(p1.comments, 0)) > 0
    #     )
    # )

    return { "new": to_list(added), "removed": to_list(removed) }


def to_list(t):
    # return list(map(lambda t: list(map(lambda x: x or "(Unknown)", t)), t))
    return list(map(list, t))

"""
Дайджест за день, за неделю
- изменения в подписчиках
- изменения в постах
- изменения в лайках
- графики для топовых/последних постов (количества просмотров, реакций и комментариев) 
- число новых просмотров и реакций за период

Текущие значения подписок и просмотров

todo: new posts
"""


def daily_digest():
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    latest_run_id = get_last_run(now)
    reference_run_id = get_last_run(yesterday)
    reference_run_id2 = get_last_run(week_ago)
    reference_run_id3 = get_last_run(month_ago)
    print(f"Latest run id: {latest_run_id}")
    print(f"Yesterday run id: {reference_run_id}")
    print(f"Last week run id: {reference_run_id2}")
    print(f"Last month run id: {reference_run_id3}")
    # print(reference_run_id, latest_run_id)
    session = SessionLocal()

    if reference_run_id:
        show_diff(latest_run_id, reference_run_id, session)
        diff_day = get_subscribers_diffs(session, reference_run_id, latest_run_id)
        print(f"Daily diff: {diff_day}")

    if reference_run_id2:
        show_diff(latest_run_id, reference_run_id2, session)
        diff_week = get_subscribers_diffs(session, reference_run_id2, latest_run_id)
        print(f"Weekly diff: {diff_week}")

    if reference_run_id3:
        show_diff(latest_run_id, reference_run_id3, session)
        diff_month = get_subscribers_diffs(session, reference_run_id3, latest_run_id)
        print(f"Monthly diff: {diff_month}")


def show_diff(latest_run_id, reference_run_id, session):
    diff = get_post_diffs(session, reference_run_id, latest_run_id)
    # print(diff)
    for row in diff:
        post_text, post_id, views_old, views_new, views_diff, reactions_old, reactions_new, reactions_diff, comments_old, comments_new, comments_diff = row
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

