import json
from glob import glob
from log_parse import parse


def test_default():
    for filename in glob('tests/*.json'):
        data = json.load(open(filename))
        params, response = data['params'], data['response']
        got = parse(**params)
        assert got == response
