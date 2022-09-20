import pytest
from golf import HitsMatch, HolesMatch, Player


holes_amounts = [*range(1, 10), 15, 46, 77, 100]


@pytest.mark.parametrize(
    'n', holes_amounts
)
def test_all_losers_hitsmatch(n):
    match = HitsMatch(n, [Player('mock') for _ in range(n)])
    iter_count = 0
    while not match.finished:
        match.hit()
        iter_count += 1
    assert iter_count == n * n * HitsMatch.PLAYER_ATTEMPTS_LIMIT


@pytest.mark.parametrize(
    'n', holes_amounts
)
def test_all_losers_holesmatch(n):
    match = HolesMatch(n, [Player('mock') for _ in range(n)])
    iter_count = 0
    while not match.finished:
        match.hit()
        iter_count += 1
    assert iter_count == n * n * HolesMatch.ATTEMPTS_PER_HOLE_LIMIT


@pytest.mark.parametrize(
    'n', holes_amounts
)
def test_all_winners_hitsmatch(n):
    match = HitsMatch(n, [Player('mock') for _ in range(n)])
    iter_count = 0
    while not match.finished:
        match.hit(True)
        iter_count += 1
    assert iter_count == n * n


@pytest.mark.parametrize(
    'n', holes_amounts
)
def test_all_winners_holesmatch(n):
    match = HolesMatch(n, [Player('mock') for _ in range(n)])
    iter_count = 0
    while not match.finished:
        match.hit(True)
        iter_count += 1
    assert iter_count == n * n
