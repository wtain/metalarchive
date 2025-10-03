from datetime import datetime, timedelta

from sqlalchemy import func

from storage_client.models import SessionLocal, BatchRun


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


def daily_digest():
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    latest_run_id = get_last_run(now)
    reference_run_id = get_last_run(yesterday)
    print(reference_run_id, latest_run_id)
