from storage_client.models import PostMetric, SessionLocal
from storage_client.posts import count_reactions


class PostsStatsDatabaseSaver:

    def __init__(self, session, batch_id):
        self.session = session
        self.records = []
        self.batch_id = batch_id

    def write_row(self, id, date, views, forwards, reactions, comments, excerpt):
        self.records.append(PostMetric(
            post_id=id,
            timestamp=date,
            views=views,
            reactions=count_reactions(reactions),  # todo: store full structure
            comments=comments,
            run_id=self.batch_id,
            # todo: add missing columns: forwards and excerpt
            # todo: separate posts table
        ))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.add_all(self.records)
        # self.session.commit()
        # self.session.close()
        print(f"✅ Posts exported to database")
