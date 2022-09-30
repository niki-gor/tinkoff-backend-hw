import os
import regex
import validators
from collections import defaultdict
from functools import lru_cache
from typing import List, Callable, Dict, Tuple
from datetime import datetime
from urllib.parse import urlparse
from http import HTTPStatus
from abc import abstractmethod, ABC


DEFAULT_LOG_PATH = 'log.log'


def parse_date(s: str) -> datetime:
    return datetime.strptime(s, parse_date.DATE_FORMAT)


parse_date.DATE_FORMAT = '%d/%b/%Y %H:%M:%S'


class Query:
    __slots__ = ('request_date',
                 'request_type',
                 'url',
                 'response_time')
    # 1 group — request_date
    # 2 group — request_type
    # 3 group — request (aka actual url)
    # omitted — protocol (not used)
    # 4 group — response_code (used only to validate and forget)
    # 5 group — response_time
    _REGEX = r'\[(.+)] "(\w+) (\S+) \S+" (\d{3}) (\d+)'
    _query_pattern = regex.compile(_REGEX)  # for optimization's sake
    _http_response_codes = set(HTTPStatus)
    _http_methods = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD',
                     'OPTIONS', 'TRACE', 'CONNECT'}

    def __init__(self,
                 request_date_str: str,
                 request_type_str: str,
                 request_str: str,
                 response_code_str: str,
                 response_time_str: str):
        self.request_date = parse_date(request_date_str)

        self.request_type = request_type_str
        if self.request_type not in self._http_methods:
            raise ValueError

        if not validators.url(request_str):
            raise ValueError
        url = urlparse(request_str)  # actual url
        self.url = url.netloc + url.path  # url according to the task

        response_code = int(response_code_str)
        if response_code not in self._http_response_codes:
            raise ValueError

        # always valid since we capture only digits in regex group
        self.response_time = int(response_time_str)

    @classmethod
    def deserialize(cls, s: str) -> 'Query':
        match = cls._query_pattern.fullmatch(s)
        if not match:
            raise ValueError
        return Query(*match.groups())


class LogStatistic(ABC):
    __slots__ = ()

    TOP_URLS_AMOUNT = 5

    def __init__(self,
                 path: str,
                 preprocessors: List[Callable[[Query], None]],
                 filters: List[Callable[[Query], bool]]):
        with open(path, 'r') as file:
            for line in file:
                line = line.strip()
                try:
                    query = Query.deserialize(line)
                except ValueError:
                    continue
                for preprocess in preprocessors:
                    preprocess(query)
                if all(requirement(query) for requirement in filters):
                    self._register_query(query)

    @abstractmethod
    def _register_query(self, query: Query):
        pass

    @property
    @abstractmethod
    def results(self) -> List[int]:
        pass


class TopUrlsStatistic(LogStatistic):
    __slots__ = '_freq'

    def __init__(self,
                 path: str,
                 preprocessors: List[Callable[[Query], None]],
                 filters: List[Callable[[Query], bool]]):
        # базовый класс считает статистику при инициализации
        # поэтому приватные переменные класса указываются до инита базового
        self._freq: Dict[str, int] = defaultdict(lambda: 0)

        super().__init__(path, preprocessors, filters)

    def _register_query(self, query: Query):
        self._freq[query.url] += 1

    # удаление элемента из списка 5 раз:                5*O(N) = O(N)
    # сортировка списка и выбор 5 элементов: O(NlogN) + 5*O(1) = O(NlogN)
    # вариант с удалением асимптотически быстрее, чем сортировка
    @property
    def results(self) -> List[int]:
        result: List[int] = []
        freq = list(self._freq.values())
        while len(freq) > 0 and len(result) < self.TOP_URLS_AMOUNT:
            max_freq = max(freq)
            freq.remove(max_freq)
            result.append(max_freq)
        return result


class SlowUrlsStatistic(LogStatistic):
    __slots__ = '_wait_freq'

    def __init__(self,
                 path: str,
                 preprocessors: List[Callable[[Query], None]],
                 filters: List[Callable[[Query], bool]]):
        self._wait_freq: Dict[str, Tuple[int, ...]] = \
            defaultdict(lambda: tuple([0, 0]))

        super().__init__(path, preprocessors, filters)

    def _register_query(self, query: Query):
        wait, freq = self._wait_freq[query.url]
        wait += query.response_time
        freq += 1
        self._wait_freq[query.url] = wait, freq

    @property
    def results(self) -> List[int]:
        result: List[int] = []
        wait_freq = list(self._wait_freq.values())
        while len(wait_freq) > 0 and len(result) < self.TOP_URLS_AMOUNT:
            max_ratio = -1
            to_remove = tuple()
            for wait, freq in wait_freq:
                if wait // freq > max_ratio:
                    max_ratio = wait // freq
                    to_remove = wait, freq
            result.append(max_ratio)
            wait_freq.remove(to_remove)
        return result


def is_not_file(query: Query) -> bool:
    return '.' not in query.url.split('/')[-1]


def is_not_ignored_url(ignored_urls: List[str]) -> Callable[[Query], bool]:
    ignored_urls_set = set(ignored_urls)

    def f(query: Query) -> bool:
        return query.url not in ignored_urls_set
    return f


def is_after(dt: datetime) -> Callable[[Query], bool]:
    def f(query: Query) -> bool:
        return query.request_date >= dt
    return f


def is_before(dt: datetime) -> Callable[[Query], bool]:
    def f(query: Query) -> bool:
        return query.request_date <= dt
    return f


def is_request_type(request_type: str) -> Callable[[Query], bool]:
    def f(query: Query) -> bool:
        return query.request_type == request_type
    return f


def remove_www_prefix(query: Query) -> None:
    if remove_www_prefix.www_pattern.match(query.url):
        query.url = regex.sub(r'www.', '', query.url, count=1)


remove_www_prefix.WWW_REGEX = r'www\.[\p{L}\d\-]+\.[\p{L}\d\-]+'
remove_www_prefix.www_pattern = regex.compile(remove_www_prefix.WWW_REGEX)


def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
) -> List[int]:
    filters: List[Callable[[Query], bool]] = []
    if ignore_files:
        filters.append(is_not_file)
    if ignore_urls:
        filters.append(is_not_ignored_url(ignore_urls))
    if start_at:
        filters.append(is_after(parse_date(start_at)))
    if stop_at:
        filters.append(is_before(parse_date(stop_at)))
    if request_type:
        filters.append(is_request_type(request_type))

    preprocessors: List[Callable[[Query], None]] = []
    if ignore_www:
        preprocessors.append(remove_www_prefix)

    statistic = TopUrlsStatistic
    if slow_queries:
        statistic = SlowUrlsStatistic

    path = os.environ.get('LOG_PATH', DEFAULT_LOG_PATH)

    return statistic(path, preprocessors, filters).results

