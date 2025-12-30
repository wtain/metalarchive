from database_saver.posts import PostsStatsDatabaseSaver
from database_saver.subscribers import SubscribersDatabaseSaver
from storage_client.models import SessionLocal, BatchRun


class DatabaseSession:

    def __init__(self, session = None):
        self.session = session if session else SessionLocal()
        self.batch_id, self.timestamp = DatabaseSession.start_batch(self.session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()

    def create_posts_saver(self):
        return PostsStatsDatabaseSaver(self.session, self.batch_id)

    def create_subscribers_saver(self):
        return SubscribersDatabaseSaver(self.session, self.timestamp, self.batch_id)

    @staticmethod
    def start_batch(session):
        batch = BatchRun()
        session.add(batch)
        session.flush()  # ensures batch.id is populated
        return batch.id, batch.timestamp

