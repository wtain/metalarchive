import logging
from functools import reduce

from sqlalchemy import delete

from aitools.tags import TagsExtractor
from aitools.title import TitleExtractor
from storage_client.models import PostMetric, Post, PostTags, PostHeader
from storage_client.posts import count_reactions


logger = logging.getLogger("uvicorn.info")


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
        # latest_run_id = self.session.query(func.max(BatchRun.id)).one()[0]
        # print(f"Latest run id: {latest_run_id}")
        # previous_values = self.session.query(
        #     PostMetric.post_id,
        #     PostMetric.views,
        #     PostMetric.comments,
        #     PostMetric.reactions
        # ).where(PostMetric.run_id == latest_run_id).all()
        # print(previous_values)

        self.session.add_all(self.records_stats)

        posts_in_db = reduce(lambda d, v: {**d, v[0]: v[1]}, map(lambda v: (v[0], v[1]), self.session.query(Post.id, Post.text).all()), {})

        ids_to_remove = posts_in_db.keys()
        posts_to_add = list(filter(lambda post: post.id not in ids_to_remove, self.records_posts))
        posts_to_update = list(filter(lambda post: post.id in posts_in_db and posts_in_db[post.id] != post.text, self.records_posts))

        self.session.execute(
            delete(Post)
            .where(Post.id.in_(map(lambda p: p.id, posts_to_update)))
        )
        self.session.add_all(posts_to_add + posts_to_update)
        logger.info(f"✅ Posts exported to database - {len(posts_to_add)} posts saved")
        logger.info(f"✅ Posts exported to database - {len(posts_to_update)} posts updated")

        logger.info("Analysing new posts")
        title_extractor = TitleExtractor()
        tags_extractor = TagsExtractor()
        for post in posts_to_add:
            post_id = post.id
            text = post.text
            tags = tags_extractor.get_tags(text)
            logger.info(f"Extracted tags: {tags}")
            title = title_extractor.get_title(text)
            logger.info(f"Extracted title: {title}")
            for name, probability in tags:
                self.session.add(PostTags(post_id=post_id, name=name, probability=probability))
            self.session.add(PostHeader(post_id=post_id, title=title))
