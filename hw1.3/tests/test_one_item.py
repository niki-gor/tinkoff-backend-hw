import os

from log_parse import parse


def test_invalid_logs():
    os.environ['LOG_PATH'] = 'tests/logs/one_item.log'
    assert parse() == [6]
    del os.environ['LOG_PATH']