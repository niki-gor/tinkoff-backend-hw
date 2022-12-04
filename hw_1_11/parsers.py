import re
from abc import ABC, abstractmethod
from typing import Optional

import requests
from bs4 import BeautifulSoup


class Parser(ABC):
    URL_REGEX: re.Pattern = None

    @classmethod
    @abstractmethod
    def parse(cls, url: str) -> str:
        pass

    @classmethod
    def can_parse(cls, url: str) -> bool:
        return bool(cls.URL_REGEX.fullmatch(url))


class YouTubeParser(Parser):
    URL_REGEX = re.compile(r'https://www\.youtube\.com/watch\?v=\w+/?')

    @classmethod
    def parse(cls, url: str) -> str:
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        result = soup.select_one('head > title').text
        return result.removesuffix(' - YouTube')


class YaMusicParser(Parser):
    URL_REGEX = re.compile(r'https://music\.yandex\.ru/album/\d+/track/\d+/?')

    @classmethod
    def parse(cls, url: str) -> str:
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        result = soup.select_one('head > title').text
        artists = soup.select_one('.page-album__artists-short > span > a').text
        return result.removesuffix(f' {artists} слушать онлайн на Яндекс Музыке')


class HabrParser(Parser):
    URL_REGEX = re.compile(r'https://habr\.com/ru/(post/|company/\w+/blog/)\d+/?')

    @classmethod
    def parse(cls, url: str) -> str:
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        result = soup.select_one('head > title').text
        return result.removesuffix(' / Хабр')


class ParserEngine:
    def __init__(self, parser: Optional[Parser] = None):
        self._parser = None
        self.set_parser(parser)

    def set_parser(self, parser: Optional[Parser]):
        if not isinstance(parser, Optional[Parser]):
            raise ValueError('Invalid argument: Parser or None expected')
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
