import itertools
import time
from collections import defaultdict
from enum import Enum

from MetalArchivesApi import MetalArchivesApi
from TelegramBotApi import TelegramBotApi

class State(Enum):
    INITIAL = 0
    REFINING_AMBIGUOUS_BAND = 1

api = TelegramBotApi()
sleep_delay_seconds = 0.5

last_seen_message = 0

metal_api = MetalArchivesApi()

client_states = defaultdict(lambda: State.INITIAL)
client_contexts = defaultdict(dict)


def reply_band_details(api, metal_api, band):
    genre = band['genre']
    country = band['country']
    name = band['name']
    similar_bands = metal_api.find_similar(band['id'])
    message = f"Name: {name}\n"
    message += f"Country: {country}\n"
    message += f"Genre: {genre}\n"
    message += "Similar bands:\n"
    similar_bands_list = list(itertools.islice(similar_bands, 10))
    for similar_band in similar_bands_list:
        name = similar_band['band_name']
        message += f"* {name}\n"
    api.send_message(chat_id, message, message_id)


while True:
    updates = api.get_updates(last_seen_message+1)

    for update in updates:
        message = update['message']
        message_id = message['message_id']
        update_id = update['update_id']
        chat_id = message['chat']['id']

        if client_states[chat_id] == State.INITIAL:
            band_name = message['text']

            bands = metal_api.search_by_name(band_name)
            if len(bands) > 100:
                api.send_message(chat_id, "Ambiguous results. Please refine the criteria.", message_id)
            elif len(bands) > 1:
                message = "Ambiguous results. Please select one of the below:\n"
                for i, band in enumerate(bands):
                    j = i + 1
                    message += f"{j}) {band['name']} ({band['country']}, {band['genre']})\n"
                api.send_message(chat_id, message, message_id)
                client_states[chat_id] = State.REFINING_AMBIGUOUS_BAND
                client_contexts[chat_id]['bands'] = bands
            elif len(bands) == 0:
                api.send_message(chat_id, f"Can't find anything for {band_name}", message_id)
            else:
                # band = metal_api.get_band(band_name)
                band = bands[0]

                reply_band_details(api, metal_api, band)
        elif client_states[chat_id] == State.REFINING_AMBIGUOUS_BAND:
            band_index = int(message['text'])-1 if message['text'].isnumeric() else -1
            bands = client_contexts[chat_id]['bands']
            if 0 <= band_index < len(bands):
                reply_band_details(api, metal_api, bands[band_index])
            else:
                api.send_message(chat_id, f"Wrong choice. The search has been reset.", message_id)
            client_states[chat_id] = State.INITIAL
        last_seen_message = max(last_seen_message, update_id)
    time.sleep(sleep_delay_seconds)