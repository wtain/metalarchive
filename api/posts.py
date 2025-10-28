from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from db.session import get_db
from storage_client.models import Post, PostMetric, BatchRun

router = APIRouter()


@router.get("/post")
def get_post(
    id: int,
    db: Session = Depends(get_db)
):
    post_data = db.query(Post.id, Post.text).filter(Post.id == id).one()
    return { "id": post_data[0], "text": post_data[1] }


@router.get("/metrics")
def get_post_metrics(id: int,
    db: Session = Depends(get_db)
):
    pm = aliased(PostMetric)
    br = aliased(BatchRun)
    query = (db.query(br.timestamp,
                    pm.views,
                    pm.reactions,
                    pm.comments
    ).join(
        br, br.id == pm.run_id
    ).filter(pm.post_id == id
    ).order_by(pm.run_id))

    return convert_data_to_json(query)

    # return list(map(lambda row: {
    #     "timestamp": row[0],
    #     "views": row[1],
    #     "reactions": row[2],
    #     "comments": row[3]
    # }, query.all()))


def convert_data_to_json(query):
    column_names = list(map(lambda desc: desc['name'], query.column_descriptions))

    def convert_row(row):
        result = {}
        for name, value in zip(column_names, row):
            result[name] = value
        return result

    data = query.all()
    return list(map(convert_row, data))
