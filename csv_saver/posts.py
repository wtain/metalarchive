import csv


class PostsStatsCsvSaver:

    def __init__(self, posts_file):
        self.file = open(posts_file, "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)
        self.writer.writerow(["message_id", "date", "views", "forwards", "reactions", "comments", "text_excerpt"])

    def write_row(self, id, date, views, forwards, reactions, comments, excerpt):
        self.writer.writerow([
            id,
            date,
            views,
            forwards,
            reactions,
            comments,
            excerpt
        ])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
