from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db

router = APIRouter()


@router.get("/changes")
def get_reactions_changes(
    period: str = "daily",  # or "weekly", "monthly"
    db: Session = Depends(get_db)
):
    """
    Returns changes in post reactions for given period.
    TODO: Replace with your implementation.
    """
    # Example placeholder
    # data = get_reactions_changes_impl(db, period)
    data = []  # <--- your logic here
    return {"period": period, "data": data}
