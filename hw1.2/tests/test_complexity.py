import pytest
import big_o
from golf import HitsMatch, HolesMatch, Player


MAX_N = 100


def f(MatchType):
    def g(n):
        match = MatchType(n, [Player('mock') for _ in range(n)])
        while not match.finished:
            match.hit()
    return g


@pytest.mark.parametrize(
    'MatchType', [HitsMatch, HolesMatch]
)
def test_complexity(MatchType):
    complexity = big_o.big_o(f(MatchType), big_o.datagen.n_, min_n=1, max_n=MAX_N)[0]
    assert isinstance(complexity, big_o.complexities.Quadratic)
