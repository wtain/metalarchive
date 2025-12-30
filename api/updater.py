import asyncio
import logging

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session

from aitools.tags import TagsExtractor
from aitools.title import TitleExtractor
from db.session import get_db
from environment.secrets import CHANNEL_NAME
from storage_client.models import Post, PostHeader, PostTags
from synchronizer.poller import poll_from_telegram

logger = logging.getLogger("uvicorn.info")

router = APIRouter()


"""
curl -X POST http://127.0.0.1:8001/api/updater/update
"""
@router.post("/update")
def update_data(
    db: Session = Depends(get_db)
):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(poll_from_telegram(db, CHANNEL_NAME))
    return result


"""
curl -X POST http://127.0.0.1:8001/api/updater/update_tags
"""
@router.post("/update_tags")
def update_tags(
    db: Session = Depends(get_db)
):
    posts = (
        db.query(Post.id.label("post_id"), Post.text)
        .filter(Post.text.isnot(None))
        .order_by(Post.id.desc())
    ).all()
    title_extractor = TagsExtractor()
    db.execute(
        delete(PostTags)
    )
    for post in posts:
        post_id = post[0]
        post_text = post[1]
        tags = title_extractor.get_tags(post_text)
        logger.info(tags)
        for name, probability in tags:
            db.add(PostTags(post_id=post_id, name=name, probability=probability))
    db.commit()

"""
curl -X POST http://127.0.0.1:8001/api/updater/update_titles
"""
@router.post("/update_titles")
def update_titles(
    db: Session = Depends(get_db)
):
    posts = (
        db.query(Post.id.label("post_id"), Post.text)
        .filter(Post.text.isnot(None))
        .order_by(Post.id.desc())
    ).all()
    title_extractor = TitleExtractor()
    db.execute(
        delete(PostHeader)
    )
    for post in posts:
        post_id = post[0]
        post_text = post[1]
        title = title_extractor.get_title(post_text)
        logger.info(title)
        db.add(PostHeader(post_id=post_id, title=title))
    db.commit()


