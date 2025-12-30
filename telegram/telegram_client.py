from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetRepliesRequest


class TelegramTelethonClient:

    def __init__(self, encrypted_session, api_id, api_hash):
        self.client = TelegramClient(encrypted_session.get_session_file(), api_id, api_hash)

    async def start(self, telegram_phone):
        # Authenticate
        await self.client.start(phone=telegram_phone)

    async def get_channel(self, channel_name):
        return await self.client.get_entity(channel_name)

    async def get_linked_chat(self, channel):
        full = await self.client(GetFullChannelRequest(channel))
        return full.chats[0] if full.chats else None  # not used actually...

    async def get_message(self, channel, message_id):
        pass

    async def list_messages(self, channel):
        async for message in self.client.iter_messages(channel, limit=200):   # adjust limit
            yield message

    async def list_participants(self, channel):
        async for user in self.client.iter_participants(channel):
            yield user

    async def get_comments(self, channel, message_id):
        try:
            result = await self.client(GetRepliesRequest(
                peer=channel,
                msg_id=message_id,
                offset_id=0,
                offset_date=None,
                add_offset=0,
                limit=20,
                max_id=0,
                min_id=0,
                hash=0
            ))
            return result
        except Exception as e:
            print(f"Error fetching comments for post {message_id}: {e}")
            return 0

    async def get_comments_count(self, channel, message_id):
        """
        Returns the number of comments for a given channel post
        """
        try:
            result = await self.client(GetRepliesRequest(
                peer=channel,
                msg_id=message_id,
                offset_id=0,
                offset_date=None,
                add_offset=0,
                limit=0,  # 0 = only count, don’t fetch messages
                max_id=0,
                min_id=0,
                hash=0
            ))
            return result.count
        except Exception as e:
            print(f"Error fetching comments for post {message_id}: {e}")
            return 0

