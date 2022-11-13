from abc import abstractmethod
from typing import Optional


class Action:
    def __init__(self, from_version: int, to_version=None):
        self.from_version = from_version
        if to_version is None:
            to_version = from_version + 1
        self.to_version = to_version

    @abstractmethod
    def apply(self, text: str) -> str:
        pass


class InsertAction(Action):
    def __init__(self, text: str, pos: Optional[int], **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.pos = pos

    def apply(self, text: str) -> str:
        if self.pos is None:
            self.pos = len(text)
        if not 0 <= self.pos <= len(text):
            raise ValueError
        return text[:self.pos] + self.text + text[self.pos:]


class ReplaceAction(Action):
    def __init__(self, text: str, pos: Optional[int], **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.pos = pos

    def apply(self, text: str) -> str:
        if self.pos is None:
            pos = len(text)
        else:
            if not 0 <= self.pos <= len(text):
                raise ValueError
            pos = self.pos
        return text[:pos] + self.text + text[pos + len(self.text):]


class DeleteAction(Action):
    def __init__(self, pos: int, length: int, **kwargs):
        super().__init__(**kwargs)
        self.pos = pos
        self.length = length

    def apply(self, text: str) -> str:
        if not 0 <= self.pos <= len(text):
            raise ValueError
        if not 0 <= self.pos + self.length <= len(text):
            raise ValueError
        return text[:self.pos] + text[self.pos + self.length:]
