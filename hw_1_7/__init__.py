import os
from os.path import join, dirname

from dotenv import load_dotenv

from .handlers import (
    Handler,
    add_favourite,
    del_favourite,
    list_favourites,
    show_info,
)

load_dotenv(join(dirname(__file__), ".env"))

TOKEN = os.environ["TOKEN"]

HANDLERS = (
    Handler("/add ", add_favourite),
    Handler("/del ", del_favourite),
    Handler("/list", list_favourites),
    Handler("", show_info),
)
