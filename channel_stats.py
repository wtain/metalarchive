import csv
import os
from datetime import datetime

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.messages import GetRepliesRequest
from telethon.tl.functions.channels import GetFullChannelRequest

from csv_saver.posts import PostsStatsCsvSaver
from csv_saver.subscribers import SubscribersCsvSaver

load_dotenv()

TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # unused now
CHANNEL_NAME = os.getenv('CHANNEL_NAME')

client = TelegramClient("session_name", TELEGRAM_API_ID, TELEGRAM_API_HASH)


async def get_post_comments_count(channel, message_id):
    """
    Returns the number of comments for a given channel post
    """
    try:
        result = await client(GetRepliesRequest(
            peer=channel,
            msg_id=message_id,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=0,     # 0 = only count, don’t fetch messages
            max_id=0,
            min_id=0,
            hash=0
        ))
        return result.count
    except Exception as e:
        print(f"Error fetching comments for post {message_id}: {e}")
        return 0


async def main():
    # Authenticate
    await client.start(phone=TELEGRAM_PHONE)

    # Replace with your channel username or ID
    channel = await client.get_entity(CHANNEL_NAME)

    full = await client(GetFullChannelRequest(channel))
    linked_chat = full.chats[0] if full.chats else None  # not used actually...

    if linked_chat:
        print(f"✅ Found linked chat: {linked_chat.title} (ID {linked_chat.id})")
    else:
        print("⚠️ This channel has no linked discussion group")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    subs_file = f"results/subscribers/subscribers_{timestamp}.csv"
    posts_file = f"results/posts/posts_{timestamp}.csv"

    await export_subscribers(channel, subs_file)

    await export_posts(channel, posts_file)


async def export_posts(channel, posts_file):

    with PostsStatsCsvSaver(posts_file) as saver:
        async for message in client.iter_messages(channel, limit=200):  # adjust limit
            excerpt = (message.text[:50] + "...") if message.text and len(message.text) > 50 else (message.text or "")
            reactions = message.reactions.to_json() if message.reactions else ""

            # Get comment count (if linked chat exists)
            comments = await get_post_comments_count(channel, message.id)

            saver.write_row(
                message.id,
                message.date,
                message.views or 0,
                message.forwards or 0,
                reactions,
                comments,
                excerpt.replace("\n", " ")
            )
    print(f"✅ Posts exported to {posts_file}")


async def export_subscribers(channel, subs_file):
    with SubscribersCsvSaver(subs_file) as saver:
        print("Fetching subscribers...")
        async for user in client.iter_participants(channel):
            saver.write_row(
                user.id,
                user.username or "",
                user.first_name or "",
                user.last_name or ""
            )
    print(f"✅ Subscribers exported to {subs_file}")


with client:
    client.loop.run_until_complete(main())

