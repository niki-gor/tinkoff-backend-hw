from typing import List

from pydantic import BaseModel


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


class Chat(BaseModel):
    id: int


class Message(BaseModel):
    chat: Chat
    text: str


class Update(BaseModel):
    message: Message
    update_id: int


class Updates(BaseModel):
    result: List[Update]
