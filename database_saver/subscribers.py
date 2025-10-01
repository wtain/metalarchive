from storage_client.models import Subscriber, SessionLocal


class SubscribersDatabaseSaver:

    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.records = []

    def write_row(self, id, username, first_name, last_name):
        self.records.append(Subscriber(
            user_id=id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            timestamp=self.timestamp,
        ))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        session = SessionLocal()
        session.add_all(self.records)
        session.commit()
        session.close()
