import os

import pytest
from log_parse import parse


@pytest.mark.parametrize('testlog', ['invalid_codes', 'invalid_time',
                                     'invalid_methods', 'invalid_domains',
                                     'invalid_dates'])
def test_invalid_logs(testlog):
    os.environ['LOG_PATH'] = f'tests/logs/{testlog}.log'
    assert parse() == []
    del os.environ['LOG_PATH']

