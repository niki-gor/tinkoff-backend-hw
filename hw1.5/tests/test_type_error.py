import os

import pytest
from tv_program import search_show


def test_type_error(capfd):
    with pytest.raises(TypeError):
        search_show(123)
    with pytest.raises(TypeError):
        search_show({})
