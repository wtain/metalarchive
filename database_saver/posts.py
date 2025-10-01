from storage_client.models import PostMetric, SessionLocal
from storage_client.posts import count_reactions


class PostsStatsDatabaseSaver:

    def __init__(self):
        self.records = []

    def write_row(self, id, date, views, forwards, reactions, comments, excerpt):
        self.records.append(PostMetric(
            post_id=id,
            timestamp=date,
            views=views,
            reactions=count_reactions(reactions),  # todo: store full structure
            comments=comments,
            # todo: add missing columns: forwards and excerpt
        ))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        session = SessionLocal()
        session.add_all(self.records)
        session.commit()
        session.close()