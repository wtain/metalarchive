import asyncio

from telethon import TelegramClient


def get_api_id():
    with open("telegram_api_id.txt") as file:
        return int(file.read())


def get_phone():
    with open("telegram_phone.txt") as file:
        return file.read()


def get_api_hash():
    with open("telegram_api_hash.txt") as file:
        return file.read()


# 1. Get your own API ID and HASH from https://my.telegram.org
api_id = get_api_id()          # <- replace with your API ID
api_hash = get_api_hash()  # <- replace with your API HASH
phone = get_phone()   # <- replace with your phone number

# 2. Create and start the client
client = TelegramClient("session_name", api_id, api_hash)

async def main():
    # Authenticate
    await client.start(phone=phone)

    # Replace with your channel username or ID
    channel = await client.get_entity("@blackholelogs")

    # ---- Get Subscribers List ----
    print("Fetching subscribers...")
    async for user in client.iter_participants(channel):
        print(f"{user.id} | {user.first_name} {user.last_name or ''} (@{user.username})")

    # ---- Get Messages (Posts) ----
    print("\nFetching channel messages...")
    async for message in client.iter_messages(channel, limit=50):  # adjust limit as needed
        print(f"ID: {message.id}")
        print(f"Date: {message.date}")
        print(f"Text: {message.text}")
        print(f"Views: {message.views}")
        print(f"Forwards: {message.forwards}")
        if message.reactions:
            print(f"Reactions: {message.reactions}")
        print("-" * 40)

with client:
    client.loop.run_until_complete(main())

