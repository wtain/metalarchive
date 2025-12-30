from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session

from db.session import get_db
from storage_client.models import PostTags

router = APIRouter()


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
