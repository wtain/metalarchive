from storage_client.models import Subscriber, SessionLocal


class SubscribersDatabaseSaver:

    def __init__(self, session, timestamp, batch_id):
        self.session = session
        self.timestamp = timestamp
        self.batch_id = batch_id
        self.records = []

    def write_row(self, id, username, first_name, last_name):
        self.records.append(Subscriber(
            user_id=id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            timestamp=self.timestamp,
            run_id=self.batch_id,
        ))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.add_all(self.records)
        # self.session.commit()
        # self.session.close()
        print(f"✅ Subscribers exported to database")
