import os

import pytest

from log_parse import parse


def test_non_existing_log():
    with pytest.raises(FileNotFoundError):
        os.environ['LOG_PATH'] = 'lol'
        parse()
    del os.environ['LOG_PATH']
