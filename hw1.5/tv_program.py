import json
import sys
from typing import Union

import pydantic.error_wrappers
import requests
from pydantic import BaseModel
from http import HTTPStatus


API_URL = "https://api.tvmaze.com/singlesearch/shows"


class Country(BaseModel):
    name: str


class Network(BaseModel):
    name: str
    country: Country


class Show(BaseModel):
    name: str
    network: Network
    summary: str

    def __str__(self):
        return (
            f"Name: {self.name}\n"
            f"Network Name: {self.network.name}\n"
            f"Network Country Name: {self.network.country.name}\n"
            f"Summary: {self.summary}"
        )


def search_show(name: str) -> Union[Show, str]:
    if not isinstance(name, str):
        raise TypeError("Expected show name (type str)")

    params = {"q": name}
    response = requests.get(url=API_URL, params=params)

    if response.status_code == HTTPStatus.NOT_FOUND:
        return "Not found"
    # не исключение — отсутствие шоу в списке — обычная ситуация

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


if __name__ == "__main__" or __name__ == "tv_program":
    showname = " ".join(sys.argv[1:])
    result = search_show(showname)
    print(result)
