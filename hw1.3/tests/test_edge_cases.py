import os

from log_parse import parse


def test_empty_log():
    os.environ['LOG_PATH'] = 'tests/logs/empty.log'
    assert parse() == []
    del os.environ['LOG_PATH']


def test_www():
    os.environ['LOG_PATH'] = 'tests/logs/www.log'
    assert parse() == [1, 1]
    assert parse(ignore_www=True) == [2]
    del os.environ['LOG_PATH']
