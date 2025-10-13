import os
from datetime import datetime

from dotenv import load_dotenv

from csv_saver.posts import PostsStatsCsvSaver
from csv_saver.subscribers import SubscribersCsvSaver
from database_saver.posts import PostsStatsDatabaseSaver
from database_saver.subscribers import SubscribersDatabaseSaver
from storage_client.models import BatchRun, SessionLocal
from telegram.TelegramSession import TelegramSession
from telegram.telegram_client import TelegramTelethonClient

load_dotenv()

TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # unused now
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
SERVER_TYPE = os.getenv('SAVER_TYPE') or 'DATABASE'
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

with TelegramSession(ENCRYPTION_KEY) as encrypted_session:

    telegram_client = TelegramTelethonClient(encrypted_session, TELEGRAM_API_ID, TELEGRAM_API_HASH)

    async def main():

        await telegram_client.start(TELEGRAM_PHONE)

        # Replace with your channel username or ID
        channel = await telegram_client.get_channel(CHANNEL_NAME)

        # cache this?
        linked_chat = await telegram_client.get_linked_chat(channel)

        if linked_chat:
            print(f"✅ Found linked chat: {linked_chat.title} (ID {linked_chat.id})")
        else:
            print("⚠️ This channel has no linked discussion group")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        subs_file = f"results/subscribers/subscribers_{timestamp}.csv"
        posts_file = f"results/posts/posts_{timestamp}.csv"

        # saver_type = 'DATABASE'

        # todo: wrap
        session = SessionLocal()
        batch_id = start_batch(session)

        await export_subscribers(channel, lambda: create_subscribers_saver(session, SERVER_TYPE, subs_file, timestamp, batch_id))

        await export_posts(channel, lambda: create_posts_saver(session, SERVER_TYPE, posts_file, timestamp, batch_id))

        session.commit()
        session.close()


    def start_batch(session):
        batch = BatchRun()
        session.add(batch)
        session.flush()  # ensures batch.id is populated
        return batch.id


    async def export_posts(channel, create_saver):

        with create_saver() as saver:
            async for message in telegram_client.list_messages(channel):
                excerpt = (message.text[:50] + "...") if message.text and len(message.text) > 50 else (message.text or "")
                reactions = message.reactions.to_json() if message.reactions else ""

                # Get comment count (if linked chat exists)
                comments = await telegram_client.get_comments_count(channel, message.id)

                saver.write_row(
                    message.id,
                    message.date,
                    message.views or 0,
                    message.forwards or 0,
                    reactions,
                    comments,
                    excerpt.replace("\n", " ")
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

