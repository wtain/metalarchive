import asyncio
import logging

from environment.media import MEDIA_PATH
from environment.secrets import ENCRYPTION_KEY, TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
from storage_client.DatabaseSession import DatabaseSession
from telegram.TelegramSession import TelegramSession
from telegram.rich_message import extract_text as extract_rich_message_text, get_message_photos
from telegram.telegram_client import TelegramTelethonClient
from telegram.web_preview import (
    download_post_image_from_web_preview,
    fetch_channel_logo_url,
    fetch_post_text_from_web_preview,
)


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


def collect_post_photos(group):
    """All downloadable Photo objects for a logical post (one or more
    Telegram messages - see group_consecutive_albums): each group member's
    regular photo, or every photo in its rich-message collage (see
    telegram/rich_message.py) when it has no regular photo."""
    photos = []
    for message in group:
        photos.extend(get_message_photos(message))
    return photos


async def download_post_images(telegram_client, group, channelName, canonical_message_id, channel_logo_url=None):
    """Downloads every photo for a logical post (collect_post_photos above),
    falling back to the web preview's og:image (telegram/web_preview.py)
    only when nothing could be downloaded natively and some group member
    still shows media Telethon couldn't decode at all - the same gap the
    text fallback below works around. channel_logo_url filters out posts
    where that fallback would just be the channel's own avatar, not real
    post content. Returns the list of saved file names, in order."""
    image_names = []
    for photo in collect_post_photos(group):
        file_name = f"{canonical_message_id}_{len(image_names)}.jpg"
        saved = await telegram_client.download_photo(photo, str(MEDIA_PATH), file_name)
        if saved:
            image_names.append(saved)

    if not image_names and any(message.media is not None for message in group):
        file_name = f"{canonical_message_id}_0.jpg"
        recovered = await asyncio.to_thread(
            download_post_image_from_web_preview,
            channelName, canonical_message_id, str(MEDIA_PATH / file_name), channel_logo_url
        )
        if recovered:
            image_names.append(file_name)

    return image_names


async def poll_from_telegram(session, channelName):

    async def export_posts(telegram_client, channel, create_saver):
        count = 0
        channel_logo_url = await asyncio.to_thread(fetch_channel_logo_url, channelName)
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
                if not post_content and message.rich_message is not None:
                    # Telegram's newer "rich message" post format (structured
                    # text + a photo collage) replaces message.text/media
                    # outright for clients recent enough to understand it -
                    # see telegram/rich_message.py.
                    post_content = extract_rich_message_text(message.rich_message)
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

                image_names = await download_post_images(
                    telegram_client, group, channelName, message.id, channel_logo_url
                )

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
    channel_logo_url = await asyncio.to_thread(fetch_channel_logo_url, channelName)
    with TelegramSession(ENCRYPTION_KEY) as encrypted_session:
        telegram_client = TelegramTelethonClient(encrypted_session, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        try:
            await telegram_client.start(TELEGRAM_PHONE)
            channel = await telegram_client.get_channel(channelName)
            for post_id in post_ids:
                message = await telegram_client.get_message(channel, post_id)
                if message is None:
                    continue
                image_names = await download_post_images(
                    telegram_client, [message], channelName, post_id, channel_logo_url
                )
                if image_names:
                    images_by_post_id[post_id] = image_names
        finally:
            await telegram_client.disconnect()
    return images_by_post_id

