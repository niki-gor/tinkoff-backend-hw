import config
from bot import Bot
from search import search_show

if __name__ == '__main__':
    bot = Bot(config.TOKEN)
    while True:
        updates = bot.get_updates()
        for update in updates:
            show_name = update.message.text
            try:
                result = str(search_show(show_name))
                result = result.replace('<p>', '').replace('</p>', '')
            except Exception as e:
                result = e.__repr__()
            sender = update.message.chat.id
            bot.send_message(sender, result)
