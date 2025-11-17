import os

from dotenv import load_dotenv

from csv_saver.posts import PostsStatsCsvSaver
from csv_saver.subscribers import SubscribersCsvSaver
from database_saver.posts import PostsStatsDatabaseSaver
from database_saver.subscribers import SubscribersDatabaseSaver
from storage_client.DatabaseSession import DatabaseSession
from telegram.TelegramSession import TelegramSession
from telegram.telegram_client import TelegramTelethonClient

load_dotenv()

TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # unused now
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
SAVER_TYPE = os.getenv('SAVER_TYPE') or 'DATABASE'
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

with TelegramSession(ENCRYPTION_KEY) as encrypted_session:
    telegram_client = TelegramTelethonClient(encrypted_session, TELEGRAM_API_ID, TELEGRAM_API_HASH)


    async def main():

        await telegram_client.start(TELEGRAM_PHONE)

        channel = await telegram_client.get_channel(CHANNEL_NAME)

        # todo: check SAVER_TYPE here and create appropriate wrapper
        with DatabaseSession() as session_wrapper:
            await export_subscribers(channel, lambda: session_wrapper.create_subscribers_saver())

            await export_posts(channel, lambda: session_wrapper.create_posts_saver())


    async def export_posts(channel, create_saver):

        with create_saver() as saver:
            async for message in telegram_client.list_messages(channel):
                reactions = message.reactions.to_json() if message.reactions else ""

                def filter_spillover_comments(iter):
                    for date, sender, message in iter:
                        if sender is not None:
                            break
                        yield message

                comments = await telegram_client.get_comments(channel, message.id)
                comments_messages = list(
                    filter_spillover_comments(
                        sorted(map(lambda c: (c.date, c.sender_id, c.message), comments.messages if comments else []))
                    )
                )
                # print(comments_messages)
                message_tail = "\n".join(comments_messages)
                post_content = message.text
                if message_tail:
                    post_content += "\n" + message_tail

                # Get comment count (if linked chat exists)
                comments_count = await telegram_client.get_comments_count(channel, message.id)

                saver.write_row(
                    message.id,
                    message.date,
                    message.views or 0,
                    message.forwards or 0,
                    reactions,
                    comments_count,
                    post_content
                )


    def create_posts_saver(session, type, posts_file, timestamp, batch_id):
        if type == 'DATABASE':
            return PostsStatsDatabaseSaver(session, batch_id)
        elif type == 'CSV':
            return PostsStatsCsvSaver(posts_file)


    def create_subscribers_saver(session, type, subs_file, timestamp, batch_id):
        if type == 'DATABASE':
            return SubscribersDatabaseSaver(session, timestamp, batch_id)
        elif type == 'CSV':
            return SubscribersCsvSaver(subs_file)


    async def export_subscribers(channel, create_saver):
        with create_saver() as saver:
            print("Fetching subscribers...")
            async for user in telegram_client.list_participants(channel):
                saver.write_row(
                    user.id,
                    user.username or "",
                    user.first_name or "",
                    user.last_name or ""
                )


    telegram_client.run_until_complete(main)
