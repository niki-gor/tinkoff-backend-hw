from .config import TOKEN
from . import HANDLERS
from .bot import Bot

if __name__ == '__main__':
    bot = Bot(TOKEN)
    while True:
        updates = bot.get_updates()
        for update in updates:
            text = update.message.text
            sender_id = update.message.chat.id

            try:
                for handler in HANDLERS:
                    if handler.route_suites(text):
                        result = handler.handle(sender_id, text)
                        break
            except Exception as e:
                result = str(e)

            bot.send_message(sender_id, result)
