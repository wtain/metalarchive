from storage_client.models import PostMetric, SessionLocal, Post
from storage_client.posts import count_reactions


class PostsStatsDatabaseSaver:

    def __init__(self, session, batch_id):
        self.session = session
        self.records_posts = []
        self.records_stats = []
        self.batch_id = batch_id

    def write_row(self, id, date, views, forwards, reactions, comments, text):
        self.records_posts.append(
            Post(id=id,
                 text=text)
        )
        self.records_stats.append(PostMetric(
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
        self.session.add_all(self.records_stats)
        ids = self.session.query(Post.id.distinct()).all()
        ids_to_remove = set(map(lambda v: v[0], ids))
        self.records_posts = list(filter(lambda post: post.id not in ids_to_remove, self.records_posts))
        self.session.add_all(self.records_posts)
        # self.session.commit()
        # self.session.close()
        print(f"✅ Posts exported to database")
