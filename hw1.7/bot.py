import json
from typing import List

import requests

from models import Update, Updates


class Bot:
    def __init__(self, token: int):
        self.token = token
        self.offset = 0

    def get_updates(self) -> List[Update]:
        url = Bot.API_URL.format(self.token, 'getUpdates')
        params = {
            'offset': self.offset,
        }
        response = requests.get(url, params=params)
        json_data = json.loads(response.content)
        result = Updates(**json_data).result
        if result:
            self.offset = result[-1].update_id + 1
        return result

    def send_message(self, chat_id: int, text: str):
        url = Bot.API_URL.format(self.token, 'sendMessage')
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'html',
        }
        print(requests.get(url, params=params).content)


Bot.API_URL = 'https://api.telegram.org/bot{}/{}'
