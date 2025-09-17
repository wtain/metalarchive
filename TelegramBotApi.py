import json

import requests

class TelegramBotApi:

    def __init__(self):
        self.token = self.get_token()

    def get_url(self, method_name):
        return f"https://api.telegram.org/bot{self.token}/{method_name}"

    def get_token(self):
        with open("telegram_token.txt") as file:
            return file.read()

    def get_updates(self, offset=None):
        url = self.get_url("getUpdates")
        params = {}
        if offset:
            params['offset'] = offset
        result = requests.get(url, params=params)

        content = json.loads(result.content)

        return content['result']

    def send_message(self, chat_id, text, reply_message_id=None):
        url = self.get_url("sendMessage")
        params = {
            'chat_id': chat_id,
            'text': text
        }
        if reply_message_id:
            params['reply_parameters'] = json.dumps({
                'message_id': reply_message_id
            })
        result = requests.get(url, params=params)
        if result.status_code // 100 != 2:
            print(f"Error(send_message): {result.status_code}")