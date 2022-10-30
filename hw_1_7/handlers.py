from typing import Callable

from .search import search_show
from .store import user_favourites


class Handler:
    def __init__(self, prefix: str, handle: Callable[[int, str], str]):
        self.prefix = prefix
        self.handle_func = handle

    def handle(self, sender_id: int, text: str) -> str:
        return self.handle_func(sender_id, text.removeprefix(self.prefix))

    def route_suites(self, text: str) -> bool:
        return text.startswith(self.prefix)


def add_favourite(sender_id: int, show_name: str) -> str:
    show = search_show(show_name)
    if not show:
        return 'Not found'
    elif show.id in user_favourites[sender_id]:
        return 'Already in favourites'
    else:
        user_favourites[sender_id][show.id] = show.name
        return 'Added to favourites: {}'.format(show.name)


def del_favourite(sender_id: int, show_name: str) -> str:
    show = search_show(show_name)
    if not show:
        return 'Not found'
    elif show.id in user_favourites[sender_id]:
        user_favourites[sender_id].pop(show.id)
        return 'Removed from favourites: {}'.format(show.name)
    else:
        return 'Not in favourites'


def list_favourites(sender_id: int, show_name: str) -> str:
    if user_favourites[sender_id]:
        return '\n'.join(user_favourites[sender_id].values())
    else:
        return 'No favourites'


def show_info(sender_id: int, show_name: str) -> str:
    show = search_show(show_name)
    if not show:
        return 'Not found'
    else:
        return str(show)
