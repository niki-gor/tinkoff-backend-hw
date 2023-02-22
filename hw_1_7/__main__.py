from .tvprogramfinder import TVProgramFinder
from . import TOKEN
from .bot import Bot

if __name__ == "__main__":
    bot = Bot(TOKEN)
    finder = TVProgramFinder(bot)
    finder.listen_and_serve()
