import asyncio
import itertools
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
)
from dotenv import load_dotenv

from MetalArchivesApi import MetalArchivesApi

load_dotenv()

TOKEN = getenv("TELEGRAM_TOKEN")

form_router = Router()


class Form(StatesGroup):
    initial_search_bands = State()
    search_disambiguate = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.initial_search_bands)
    await message.answer(
        "Hi! Enter metal band name to search"
    )

async def reply_band_details(message: Message, metal_api, band):
    genre = band['genre']
    country = band['country']
    name = band['name']
    similar_bands = metal_api.find_similar(band['id'])
    response = f"Name: {name}\n"
    response += f"Country: {country}\n"
    response += f"Genre: {genre}\n"
    response += "Similar bands:\n"
    similar_bands_list = list(itertools.islice(similar_bands, 10))
    for similar_band in similar_bands_list:
        name = similar_band['band_name']
        response += f"* {name}\n"
    await message.answer(response, reply_to_message_id=message.message_id)


@form_router.message(Form.search_disambiguate)
async def process_dont_like_write_bots(message: Message, state: FSMContext) -> None:
    index_string = message.text
    band_index = int(index_string) - 1 if index_string.isnumeric() else -1
    data = await state.get_data()
    await state.clear()
    bands = data['bands']
    if 0 <= band_index < len(bands):
        metal_api = MetalArchivesApi()
        await reply_band_details(message, metal_api, bands[band_index])
    else:
        await message.answer(f"Wrong choice. The search has been reset.")
    await state.set_state(Form.initial_search_bands)

@form_router.message()
@form_router.message(Form.initial_search_bands)
async def process_band_name(message: Message, state: FSMContext) -> None:
    band_name = message.text
    await state.update_data(band_name=band_name)

    metal_api = MetalArchivesApi()

    bands = metal_api.search_by_name(band_name)
    if len(bands) > 30:
        await message.answer("Ambiguous results. Please refine the criteria.", reply_to_message_id=message.message_id)
    elif len(bands) > 1:
        response = "Ambiguous results. Please select one of the below:\n"
        for i, band in enumerate(bands):
            j = i + 1
            response += f"{j}) {band['name']} ({band['country']}, {band['genre']})\n"
        await message.answer(response, reply_to_message_id=message.message_id)
        await state.set_state(Form.search_disambiguate)
        await state.update_data(bands=bands)
    elif len(bands) == 0:
        await message.answer(f"Can't find anything for {band_name}", reply_to_message_id=message.message_id)
    else:
        band = bands[0]

        await reply_band_details(message, metal_api, band)


async def main():
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()

    dp.include_router(form_router)

    # Start event dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
