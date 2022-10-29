import json
from typing import List

import requests

from models import Update, Updates


ALLOWED_TAGS = ('b', 'strong',
                'i', 'em',
                'u', 'ins',
                's', 'strike',
                'span', 'tg-spoiler',
                'a',
                'code',
                'pre')


def _remove_unsupported_tags(s: str) -> str:
    result = ''
    idx = 0

    while idx < len(s):
        if s[idx] != '<':
            result += s[idx]
            idx += 1
        else:
            closing_idx = s.find('>', idx)
            if closing_idx == -1:
                return s
            tag = s[idx+1:closing_idx].split()[0].removeprefix('/')
            if tag in ALLOWED_TAGS:
                result += s[idx:closing_idx+1]
            idx = closing_idx + 1

    return result


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
        text = _remove_unsupported_tags(text)
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'html',
        }
        requests.get(url, params=params)


Bot.API_URL = 'https://api.telegram.org/bot{}/{}'
