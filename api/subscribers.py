from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from storage_client.subscribers import subscribers_count_over_time

router = APIRouter()


@router.get("/count-over-time")
def get_subscribers_count_over_time(
    period: str = "daily",  # or "weekly", "monthly"
    db: Session = Depends(get_db)
):
    # todo: pass db into this
    # data = list(map(lambda t: [t[0], t[1]], subscribers_count_over_time()))
    data = subscribers_count_over_time()
    return {"period": period, "data": data}

