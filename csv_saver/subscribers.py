import csv


class SubscribersCsvSaver:

    def __init__(self, subs_file):
        self.file = open(subs_file, "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)
        self.writer.writerow(["user_id", "username", "first_name", "last_name"])

    def write_row(self, id, username, first_name, last_name):
        self.writer.writerow([
            id,
            username,
            first_name,
            last_name
        ])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
