from .handlers import Handler, add_favourite, del_favourite, list_favourites, show_info

HANDLERS = (
    Handler('/add ', add_favourite),
    Handler('/del ', del_favourite),
    Handler('/list', list_favourites),
    Handler('', show_info),
)
