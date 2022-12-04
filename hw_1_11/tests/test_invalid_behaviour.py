import pytest

from ..parsers import ParserFactory, ParserEngine, YouTubeParser


ok_url = 'https://www.youtube.com/watch?v=90RLzVUuXe4'
bad_url = 'hello world'


def test_bad_urls():
    parser = ParserFactory.get_parser(bad_url)  # must be None
    pe = ParserEngine(parser)
    with pytest.raises(RuntimeError):
        pe.parse(ok_url)


def test_unconfigured():
    pe = ParserEngine()
    with pytest.raises(RuntimeError):
        pe.parse(ok_url)


def test_invalid_parser():
    invalid_parser = 'not_parser'
    with pytest.raises(ValueError):
        pe = ParserEngine(invalid_parser)
    pe = ParserEngine()
    with pytest.raises(ValueError):
        pe.set_parser(invalid_parser)
