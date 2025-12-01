
from environment.secrets import ENCRYPTION_KEY, TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE, CHANNEL_NAME
from storage_client.DatabaseSession import DatabaseSession
from telegram.TelegramSession import TelegramSession
from telegram.telegram_client import TelegramTelethonClient


async def poll_from_telegram(channelName):

    async def export_posts(telegram_client, channel, create_saver):

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
                        sorted(
                            map(lambda c: (c.date, c.sender_id, c.message), comments.messages if comments else []))
                    )
                )

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

    async def export_subscribers(telegram_client, channel, create_saver):
        with create_saver() as saver:
            print("Fetching subscribers...")
            async for user in telegram_client.list_participants(channel):
                saver.write_row(
                    user.id,
                    user.username or "",
                    user.first_name or "",
                    user.last_name or ""
                )

    with TelegramSession(ENCRYPTION_KEY) as encrypted_session:
        telegram_client = TelegramTelethonClient(encrypted_session, TELEGRAM_API_ID, TELEGRAM_API_HASH)

        await telegram_client.start(TELEGRAM_PHONE)

        channel = await telegram_client.get_channel(channelName)

        # todo: check SAVER_TYPE here and create appropriate wrapper
        with DatabaseSession() as session_wrapper:
            await export_subscribers(telegram_client, channel, lambda: session_wrapper.create_subscribers_saver())

            await export_posts(telegram_client, channel, lambda: session_wrapper.create_posts_saver())

