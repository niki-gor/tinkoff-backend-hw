import os
from log_parse import parse


def test_russian_domains():
    os.environ['LOG_PATH'] = 'tests/logs/russian_sites.log'
    assert parse(ignore_www=True) == [2, 1]
    del os.environ['LOG_PATH']
