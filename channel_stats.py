import asyncio
import csv
from datetime import datetime

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

channel_name = "@blackholelogs"

async def main():
    # Authenticate
    await client.start(phone=phone)

    # Replace with your channel username or ID
    channel = await client.get_entity(channel_name)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    subs_file = f"subscribers_{timestamp}.csv"
    posts_file = f"posts_{timestamp}.csv"

    # ---- Get Subscribers List ----
    print("Fetching subscribers...")

    # --- Export Subscribers ---
    with open(subs_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "username", "first_name", "last_name"])
        async for user in client.iter_participants(channel):
            writer.writerow([
                user.id,
                user.username or "",
                user.first_name or "",
                user.last_name or ""
            ])
    print(f"✅ Subscribers exported to {subs_file}")

    # --- Export Posts ---
    with open(posts_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["message_id", "date", "views", "forwards", "reactions", "text_excerpt"])
        async for message in client.iter_messages(channel, limit=200):  # adjust limit
            excerpt = (message.text[:50] + "...") if message.text and len(message.text) > 50 else (message.text or "")
            reactions = message.reactions.to_json() if message.reactions else ""
            writer.writerow([
                message.id,
                message.date,
                message.views or 0,
                message.forwards or 0,
                reactions,
                excerpt.replace("\n", " ")
            ])
    print(f"✅ Posts exported to {posts_file}")

with client:
    client.loop.run_until_complete(main())

