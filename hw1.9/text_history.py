from typing import Optional

from actions import InsertAction, ReplaceAction, DeleteAction, Action


class TextHistory:
    def __init__(self):
        self._text = ''
        self._version = 0
        self._actions = []

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def insert(self, text: str, pos=None) -> int:
        action = InsertAction(text,
                              pos,
                              from_version=self._version)
        return self.action(action)

    def replace(self, text: str, pos=None) -> int:
        action = ReplaceAction(text,
                               pos,
                               from_version=self._version)
        return self.action(action)

    def delete(self, pos: int, length: int) -> int:
        action = DeleteAction(pos,
                              length,
                              from_version=self._version)
        return self.action(action)

    def action(self, action: Action) -> int:
        if self.version != action.from_version:
            raise ValueError
        self._text = action.apply(self._text)
        self._version = action.to_version
        self._actions.append(action)
        return self._version

    def get_actions(self, from_version=None, to_version=None):
        if from_version is None:
            from_version = 0
        if to_version is None:
            to_version = self._version

        if from_version < 0 or to_version > self._version:
            raise ValueError
        if from_version > to_version:
            raise ValueError

        for start, action in enumerate(self._actions):
            if action.from_version >= from_version:
                break
        else:
            start = len(self._actions)

        for end, action in enumerate(self._actions[start:], start):
            if action.to_version > to_version:
                break
        else:
            end = len(self._actions)

        return self._actions[start:end]
