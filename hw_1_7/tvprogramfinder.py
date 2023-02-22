from typing import Optional

from . import HANDLERS
from .bot import Bot


class TVProgramFinder:
    def __init__(self, bot: Bot):
        self.bot = bot

    def listen_and_serve(self):
        while True:
            updates = self.bot.get_updates()
            for update in updates:
                sender_id = update.message.chat.id
                text = update.message.text

                result = self._handle_update(sender_id, text)

                if result is not None:
                    self.bot.send_message(sender_id, result)

    def _handle_update(self, sender_id: int, text: str) -> Optional[str]:
        result = None
        try:
            for handler in HANDLERS:
                if handler.route_suites(text):
                    result = handler.handle(sender_id, text)
                    break
        except Exception as e:
            result = str(e)
        return result
