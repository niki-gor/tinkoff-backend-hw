import re
from abc import ABC
from typing import Optional

import requests
from bs4 import BeautifulSoup


class Parser(ABC):
    URL_REGEX: re.Pattern = None
    SELECTOR: str = None

    @classmethod
    def parse(cls, url: str) -> str:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        result = soup.select_one(cls.SELECTOR)
        return result.text

    @classmethod
    def can_parse(cls, url: str) -> bool:
        return bool(cls.URL_REGEX.fullmatch(url))


class TitleParser(Parser):
    SELECTOR = 'head > title'
    REMOVESUFFIX: str = None

    @classmethod
    def parse(cls, url: str) -> str:
        return super().parse(url).removesuffix(cls.REMOVESUFFIX)


class YouTubeParser(TitleParser):
    URL_REGEX = re.compile(r'https://www\.youtube\.com/watch\?v=\w+/?')
    REMOVESUFFIX = ' - YouTube'


class YaMusicParser(TitleParser):
    URL_REGEX = re.compile(r'https://music\.yandex\.ru/album/\d+/track/\d+/?')
    REMOVESUFFIX = ' слушать онлайн на Яндекс Музыке'

    @classmethod
    def parse(cls, url: str) -> str:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        result = soup.select_one(cls.SELECTOR).text
        artists = soup.select_one('.page-album__artists-short > span > a').text
        return result.removesuffix(f' {artists}{cls.REMOVESUFFIX}')


class HabrParser(TitleParser):
    URL_REGEX = re.compile(r'https://habr\.com/ru/post/\d+/?')
    REMOVESUFFIX = ' / Хабр'


class ParserEngine:
    def __init__(self, parser: Optional[Parser] = None):
        self._parser = parser

    def set_parser(self, parser):
        self._parser = parser

    def parse(self, url) -> str:
        try:
            return self._parser.parse(url)
        except AttributeError:
            raise RuntimeError('Parser must be set')


class ParserFactory:
    PARSERS = (
        YouTubeParser,
        YaMusicParser,
        HabrParser,
    )

    @classmethod
    def get_parser(cls, url) -> Optional[Parser]:
        for parser in cls.PARSERS:
            if parser.can_parse(url):
                return parser()
        return None
