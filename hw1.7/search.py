import json
from http import HTTPStatus
from typing import Union

import pydantic
import requests

from models import Show


def search_show(name: str) -> Union[Show, str]:
    if not isinstance(name, str):
        raise TypeError("Expected show name (type str)")

    params = {"q": name}
    response = requests.get(url=search_show.API_URL, params=params)

    if response.status_code == HTTPStatus.NOT_FOUND:
        return "Not found"
    # не является исключением. отсутствие шоу в списке — обычная ситуация

    if response.status_code != HTTPStatus.OK:
        raise Exception(
            f"Something bad happened: {response.status_code}\n"
            f"{response.content!r}"
        )

    try:
        json_data = json.loads(response.content)
        show = Show(**json_data)
    except json.decoder.JSONDecodeError:
        raise ValueError("Invalid JSON response")
    except pydantic.error_wrappers.ValidationError:
        raise ValueError("Missing required fields")

    return show


search_show.API_URL = "https://api.tvmaze.com/singlesearch/shows"
