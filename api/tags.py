from fastapi import APIRouter, Depends
from sqlalchemy import delete, func
from sqlalchemy.orm import Session

from db.session import get_db
from storage_client.models import PostTags

router = APIRouter()


@router.get("/cloud")
def get_tag_cloud(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(PostTags.name, func.count(PostTags.id).label("count"))
        .group_by(PostTags.name)
        .order_by(func.count(PostTags.id).desc())
        .all()
    )
    return [{"name": name, "count": count} for name, count in rows]


@router.post("/add")
def add_tag(
    post_id: int,
    name: str,
    db: Session = Depends(get_db)
):
    tag = PostTags(post_id=post_id, name=name, probability=1.0)
    db.add(tag)
    db.commit()
    return { "id": tag.id, "name": tag.name }


@router.delete("/delete")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    db.execute(delete(PostTags).where(PostTags.id == tag_id))
    db.commit()
