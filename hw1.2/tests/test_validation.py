import pytest
from golf import HitsMatch, HolesMatch, Player


@pytest.mark.parametrize(
    'MatchType', [HitsMatch, HolesMatch]
)
def test_values(MatchType):
    with pytest.raises(ValueError):
        MatchType(0, [])  # считаем матч без игроков невалидным
    with pytest.raises(ValueError):
        MatchType(0, [Player('mock')])
    with pytest.raises(ValueError):
        MatchType(-1, [Player('mock')])
    with pytest.raises(ValueError):
        MatchType(7777777777777777, [Player('mock')])
