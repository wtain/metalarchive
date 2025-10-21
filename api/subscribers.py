from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db

router = APIRouter()


@router.get("/count-over-time")
def get_subscribers_count_over_time(
    period: str = "daily",  # or "weekly", "monthly"
    db: Session = Depends(get_db)
):
    """
    Returns total subscribers count change over time.
    TODO: Replace with your implementation.
    """
    # Example placeholder
    # data = get_subscribers_count_over_time_impl(db, period)
    data = []  # <--- your logic here
    return {"period": period, "data": data}


@router.get("/changes")
def get_subscribers_changes(
    period: str = "daily",  # or "weekly", "monthly"
    db: Session = Depends(get_db)
):
    """
    Returns changes in subscribers (added/removed) for given period.
    TODO: Replace with your implementation.
    """
    # Example placeholder
    # data = get_subscribers_changes_impl(db, period)
    data = []  # <--- your logic here
    return {"period": period, "data": data}
