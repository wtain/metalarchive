import asyncio
import datetime
from os import getenv

from aiogram import filters
from aiogram.handlers import MessageHandler
from aiohttp.abc import Application
from dotenv import load_dotenv


async def fetch_and_process_updates(app):
    offset = None
    bot = app.bot

    while True:
        updates = await bot.get_updates(offset=offset, timeout=10, allowed_updates=["message",
                                                                                    "edited_channel_post", "callback_query", "message_reaction"])
        if len(updates) > 0:
            print('Received ' + str(len(updates)) + ' updates at ' + str(datetime.datetime.now()))
        for update in updates:
            print(update)
            await app.process_update(update)

            offset = update.update_id + 1

        await asyncio.sleep(1)


async def main():
    load_dotenv()

    TOKEN = getenv("TELEGRAM_TOKEN")

    app = Application.builder().token(TOKEN).build()
    # app.add_handler(CommandHandler(...))
    # app.add_handler(MessageHandler(filters.TEXT, ...))
    app.add_handler(MessageHandler(filters.TEXT))

    await app.initialize()
    print("Bot is running...")

    await fetch_and_process_updates(app)


asyncio.run(main())
