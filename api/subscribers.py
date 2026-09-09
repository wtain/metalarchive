from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from storage_client.subscribers import subscribers_count_over_time, get_subscriber_changes

router = APIRouter()

PERIOD_TO_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}


@router.get("/count-over-time")
def get_subscribers_count_over_time(
    period: str = "",  # or "daily", "weekly", "monthly"
    db: Session = Depends(get_db)
):
    # todo: pass db into this
    # data = list(map(lambda t: [t[0], t[1]], subscribers_count_over_time()))
    # period - is ignored for now
    data = subscribers_count_over_time(period, db)
    return {"period": period, "data": data}


@router.get("/changes")
def get_subscribers_changes(
    period: str = "daily",  # or "weekly", "monthly"
    db: Session = Depends(get_db)
):
    end = datetime.now()
    start = end - timedelta(days=PERIOD_TO_DAYS.get(period, 1))
    changes = get_subscriber_changes(db, start, end)
    return {"period": period, **changes}

