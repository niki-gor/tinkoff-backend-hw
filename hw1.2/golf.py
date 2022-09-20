import queue
from abc import abstractmethod, ABC
from functools import lru_cache
from itertools import chain
from typing import Iterator, Tuple, List, Optional


class Player:
    def __init__(self, name: str):
        self.name = name


class Table:
    def __init__(self, headers: List[Player], rows: int):
        self.headers = headers
        self.rows_amount = rows
        cols_amount = len(headers)
        self.table = [[None for j in range(cols_amount)] for i in range(rows)]

    def _column_names(self) -> Tuple[str, ...]:
        return tuple([header.name for header in self.headers])

    def get(self) -> List[Tuple]:
        return [self._column_names(), *[tuple(row) for row in self.table]]

    def __getitem__(self, row) -> List[Optional[int]]:
        return self.table[row]


class BaseMatch(ABC):
    __slots__ = 'finished', '_holes_amount', '_players_amount', \
        '_scores_table', '_chan', '_hit'

    def __init__(self, holes_amount: int, players: List[Player]):
        if holes_amount != len(players):
            raise ValueError
        if not players:
            raise ValueError
        self.finished = False
        self._holes_amount = holes_amount
        self._players_amount = len(players)
        self._scores_table = Table(players, holes_amount)
        self._chan = queue.Queue()
        self._hit = self._hit_worker(self._chan)
        next(self._hit)

    @abstractmethod
    def _hit_worker(self, chan: queue.Queue) -> Iterator[None]:
        pass

    @abstractmethod
    def _win_criteria(self, scores: List[int]) -> int:
        pass

    def hit(self, success: bool = False) -> None:
        if self.finished:
            raise RuntimeError
        self._chan.put(success)
        try:
            next(self._hit)
        except StopIteration:
            self.finished = True

    @lru_cache  # not_finished -> finished   OK         finished -> not_finished   UNREACHABLE
    def get_winners(self) -> List[Player]:  # следовательно lru_cache OK
        if not self.finished:
            raise RuntimeError
        player_sums = [sum(col) for col in zip(*self._scores_table)]
        winner_sum = self._win_criteria(player_sums)
        players = self._scores_table.headers
        result = []
        for player_idx, player_sum in enumerate(player_sums):
            if player_sum == winner_sum:
                result.append(players[player_idx])
        return result

    def get_table(self) -> List[Tuple[int]]:
        return self._scores_table.get()

    def _player_indices_from(self, hole_idx: int) -> Iterator[int]:
        return chain(range(hole_idx, self._players_amount), range(hole_idx))


class HitsMatch(BaseMatch):
    __slots__ = ()

    PLAYER_ATTEMPTS_LIMIT = 9
    LOSER_SCORE = 10

    def __init__(self, holes_amount: int, players: List[Player]):
        super().__init__(holes_amount, players)

    def _hit_worker(self, chan: queue.Queue) -> None:
        for hole_idx in range(self._holes_amount):
            hole_scores = self._scores_table[hole_idx]
            for attempts_count in range(self.PLAYER_ATTEMPTS_LIMIT):
                for player_idx in self._player_indices_from(hole_idx):
                    if hole_scores[player_idx] is not None:
                        continue
                    yield
                    success = chan.get()
                    if success:
                        hole_scores[player_idx] = attempts_count + 1
            for player_idx in self._player_indices_from(hole_idx):
                if hole_scores[player_idx] is None:
                    hole_scores[player_idx] = self.LOSER_SCORE

    def _win_criteria(self, scores: List[int]) -> int:
        return min(scores)


class HolesMatch(BaseMatch):
    __slots__ = ()

    ATTEMPTS_PER_HOLE_LIMIT = 10
    LOSER_SCORE = 0

    def __init__(self, holes_amount: int, players: List[Player]):
        super().__init__(holes_amount, players)

    def _hit_worker(self, chan: queue.Queue) -> None:
        for hole_idx in range(self._holes_amount):
            hole_scores = self._scores_table[hole_idx]
            for attempts_count in range(self.ATTEMPTS_PER_HOLE_LIMIT):
                someone_successful = False
                for player_idx in self._player_indices_from(hole_idx):
                    if hole_scores[player_idx] is not None:
                        continue
                    yield
                    success = chan.get()
                    if success:
                        someone_successful = True
                        hole_scores[player_idx] = 1
                if someone_successful:
                    break
            for player_idx in self._player_indices_from(hole_idx):
                if hole_scores[player_idx] is None:
                    hole_scores[player_idx] = self.LOSER_SCORE

    def _win_criteria(self, scores: List[int]) -> int:
        return max(scores)
