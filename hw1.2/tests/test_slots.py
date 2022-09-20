import pytest
from golf import HitsMatch, HolesMatch, Player


@pytest.mark.parametrize(
    'MatchType', [HitsMatch, HolesMatch]
)
def test_unwanted_fields(MatchType):
    match = MatchType(1, [Player('mock')])
    with pytest.raises(AttributeError):
        match.unwanted_field = 42
    with pytest.raises(AttributeError):
        match.lololololol = 1337
