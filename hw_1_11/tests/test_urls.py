import pytest as pytest

from ..parsers import ParserEngine, ParserFactory


@pytest.mark.parametrize(
    'url, expected', (
            ('https://www.youtube.com/watch?v=90RLzVUuXe4',
             'David Guetta & Bebe Rexha - I\'m Good (Blue) [Official Music Video]'),
            ('https://music.yandex.ru/album/13707793/track/60292250', 'Blinding Lights'),
            ('https://habr.com/ru/post/280238/', 'Web Scraping с помощью python'),
    ),
)
def test_basic_urls(url, expected):
    pe = ParserEngine()
    parser = ParserFactory.get_parser(url)
    pe.set_parser(parser)
    assert pe.parse(url) == expected
