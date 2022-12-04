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


@pytest.mark.parametrize(
    'url, expected', (
            ('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'Rick Astley - Never Gonna Give You Up (Official Music Video)'),
            ('https://www.youtube.com/watch?v=sOnqjkJTMaA', 'Michael Jackson - Thriller (Official 4K Video)'),
            ('https://music.yandex.ru/album/1917143/track/10776528', 'New Kid in Town'),
            ('https://music.yandex.ru/album/3216/track/38884', 'Happy New Year'),
            ('https://habr.com/ru/company/productivity_inside/blog/703038/', 'Когда о человеке можно сказать, что он стал программистом?'),
            ('https://habr.com/ru/company/productivity_inside/blog/699430/', 'История скромного успеха моей первой за десять лет инди-игры')
    ),
)
def test_other_urls(url, expected):
    pe = ParserEngine()
    parser = ParserFactory.get_parser(url)
    pe.set_parser(parser)
    assert pe.parse(url) == expected
