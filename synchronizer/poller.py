import asyncio
import logging

from environment.media import MEDIA_PATH
from environment.secrets import ENCRYPTION_KEY, TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
from storage_client.DatabaseSession import DatabaseSession
from telegram.TelegramSession import TelegramSession
from telegram.telegram_client import TelegramTelethonClient
from telegram.web_preview import fetch_post_text_from_web_preview


logger = logging.getLogger("uvicorn.info")


async def group_consecutive_albums(messages):
    """Groups consecutive Telegram messages sharing a grouped_id - the classic
    multi-message photo album - into one list; everything else becomes a
    single-element list. Relies on iter_messages() returning album members
    adjacently, which holds for a single unpaginated channel fetch since
    they're created together and share a timestamp."""
    pending = []
    async for message in messages:
        if pending and message.grouped_id != pending[-1].grouped_id:
            yield pending
            pending = []
        pending.append(message)
        if message.grouped_id is None:
            yield pending
            pending = []
    if pending:
        yield pending


def pick_canonical_message(group):
    # Exactly one message in an album usually carries the caption; fall back
    # to the first if none do (group is a list of one for non-album posts).
    return next((message for message in group if message.text), group[0])


async def poll_from_telegram(session, channelName):

    async def export_posts(telegram_client, channel, create_saver):
        count = 0
        with create_saver() as saver:
            logger.info("Loading posts...")
            async for group in group_consecutive_albums(telegram_client.list_messages(channel)):
                message = pick_canonical_message(group)
                reactions = message.reactions.to_json() if message.reactions else ""

                def filter_spillover_comments(iter):
                    for date, sender, message in iter:
                        if sender is not None:
                            break
                        yield message

                comments = await telegram_client.get_comments(channel, message.id)
                comments_messages = list(
                    filter_spillover_comments(
                        sorted(
                            map(lambda c: (c.date, c.sender_id, c.message), comments.messages if comments else []))
                    )
                )

                message_tail = "\n".join(comments_messages)
                post_content = message.text
                if not post_content and message.media is not None:
                    # Telethon (and even Telegram's own web client) can't
                    # render some newer message formats - see
                    # telegram/web_preview.py for the full story. message.media
                    # not None but text empty is the signal something's
                    # there we're just not capturing; run_in_executor-style
                    # to_thread keeps this blocking HTTP call off the event
                    # loop other Telegram I/O for this poll depends on.
                    post_content = await asyncio.to_thread(
                        fetch_post_text_from_web_preview, channelName, message.id
                    ) or post_content
                if message_tail:
                    post_content += "\n" + message_tail

                # Get comment count (if linked chat exists)
                comments_count = await telegram_client.get_comments_count(channel, message.id)

                image_names = []
                for index, group_message in enumerate(group):
                    file_name = await telegram_client.download_photo(
                        group_message, str(MEDIA_PATH), f"{message.id}_{index}.jpg"
                    )
                    if file_name:
                        image_names.append(file_name)

                saver.write_row(
                    message.id,
                    message.date,
                    message.views or 0,
                    message.forwards or 0,
                    reactions,
                    comments_count,
                    post_content,
                    image_names
                )
                count += 1
        return count

    async def export_subscribers(telegram_client, channel, create_saver):
        count = 0
        with create_saver() as saver:
            logger.info("Fetching subscribers...")
            async for user in telegram_client.list_participants(channel):
                saver.write_row(
                    user.id,
                    user.username or "",
                    user.first_name or "",
                    user.last_name or ""
                )
                count += 1
        return count

    with TelegramSession(ENCRYPTION_KEY) as encrypted_session:
        telegram_client = TelegramTelethonClient(encrypted_session, TELEGRAM_API_ID, TELEGRAM_API_HASH)

        try:
            await telegram_client.start(TELEGRAM_PHONE)

            channel = await telegram_client.get_channel(channelName)

            with DatabaseSession(session) as session_wrapper:
                f1 = export_subscribers(telegram_client, channel, lambda: session_wrapper.create_subscribers_saver())

                f2 = export_posts(telegram_client, channel, lambda: session_wrapper.create_posts_saver())

                logger.info(f"Waiting for background tasks to complete")
                results = await asyncio.gather(f1, f2)
                logger.info(f"Results {results}")
                return results
        finally:
            # Without this, the client's connection keepalive/update-loop
            # tasks are left dangling on this call's event loop once the
            # function returns. They get garbage-collected at some later,
            # unpredictable point (often during the NEXT poll's blocking AI
            # step, since that's what starves this loop long enough for
            # Telegram's keepalive to lapse and trigger a reconnect attempt
            # on a loop that's by then been torn down) - producing "Task was
            # destroyed but it is pending!" / "Event loop is closed" noise
            # and leaking the underlying TCP connection to Telegram.
            await telegram_client.disconnect()


async def backfill_images(post_ids, channelName):
    """One-time recovery of images for posts that were scraped before image
    downloading existed - unlike poll_from_telegram, this has to refetch each
    message from Telegram since its photo was never downloaded originally.
    Returns {post_id: [file_name, ...]} for posts whose photo was recovered."""
    images_by_post_id = {}
    with TelegramSession(ENCRYPTION_KEY) as encrypted_session:
        telegram_client = TelegramTelethonClient(encrypted_session, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        try:
            await telegram_client.start(TELEGRAM_PHONE)
            channel = await telegram_client.get_channel(channelName)
            for post_id in post_ids:
                message = await telegram_client.get_message(channel, post_id)
                if message is None:
                    continue
                file_name = await telegram_client.download_photo(message, str(MEDIA_PATH), f"{post_id}_0.jpg")
                if file_name:
                    images_by_post_id[post_id] = [file_name]
        finally:
            await telegram_client.disconnect()
    return images_by_post_id

