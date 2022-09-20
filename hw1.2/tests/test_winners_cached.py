import pytest
from golf import HitsMatch, HolesMatch, Player


HOLES_AMOUNT = 100
MANY_TIMES = 1000000


def finished_hitsmatch():
    match = HitsMatch(HOLES_AMOUNT, [Player('mock') for _ in range(HOLES_AMOUNT)])
    while not match.finished:
        match.hit()
    return match


def finished_holesmatch():
    match = HolesMatch(HOLES_AMOUNT, [Player('mock') for _ in range(HOLES_AMOUNT)])
    while not match.finished:
        match.hit()
    return match


@pytest.mark.parametrize(
    'match', [finished_hitsmatch(), finished_holesmatch()]
)
@pytest.mark.timeout(1)
def test_cached(match):
    for _ in range(MANY_TIMES):
        match.get_winners()  # без @lru_cache не пройдет по времени
