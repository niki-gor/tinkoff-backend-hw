import json
import sys

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


def search_show(name: str):
    if not isinstance(name, str):
        raise TypeError("Expected show name (type str)")

    params = {"q": name}
    response = requests.get(url=API_URL, params=params)

    if response.status_code == HTTPStatus.NOT_FOUND:
        print("Not found")
        return

    try:
        json_data = json.loads(response.content)
    except json.decoder.JSONDecodeError:
        print("Invalid JSON response")
        return

    try:
        show = Show(**json_data)
    except pydantic.error_wrappers.ValidationError:
        print("Missing required fields")
        return

    print(show)


if __name__ == "__main__" or __name__ == "tv_program":
    search_show(" ".join(sys.argv[1:]))
