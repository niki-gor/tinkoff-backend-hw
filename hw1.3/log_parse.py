import re
from collections import defaultdict
from functools import lru_cache
from typing import List, Callable, Dict, Tuple
from datetime import datetime
from furl import furl
from http import HTTPStatus
from abc import abstractmethod, ABC


_LOG_PATH = 'log.log'
_DATE_FORMAT = '%d/%b/%Y %H:%M:%S'


def parse_date(s: str) -> datetime:
    return datetime.strptime(s, _DATE_FORMAT)


class Query:
    __slots__ = ('request_date',
                 'request_type',
                 'request',
                 'protocol',
                 'response_code',
                 'response_time')

    _REGEX = r'\[(.+)] "(\w+) (\S+) (\S+)" (\d{3}) (\d+)'
    _query_pattern = re.compile(_REGEX)  # для ускорения работы
    _http_response_codes = set(HTTPStatus)

    def __init__(self,
                 request_date_str,
                 request_type_str,
                 request_str,
                 protocol_str,
                 response_code_str,
                 response_time_str):
        self.request_date = parse_date(request_date_str)
        self.request_type = request_type_str
        self.request = furl(request_str)
        self.protocol = protocol_str
        self.response_code = int(response_code_str)
        if self.response_code not in self._http_response_codes:
            raise ValueError
        self.response_time = int(response_time_str)

    @property
    def url(self) -> str:
        return self.request.netloc + self.request.pathstr

    @classmethod
    def deserialize(cls, s: str) -> 'Query':
        match = cls._query_pattern.fullmatch(s)
        if not match:
            raise ValueError
        return Query(*match.groups())


class LogStatistic(ABC):
    __slots__ = ('_path',
                 '_preprocessors',
                 '_filters')

    TOP_URLS_AMOUNT = 5

    def __init__(self,
                 path: str,
                 preprocessors: List[Callable[[Query], None]],
                 filters: List[Callable[[Query], bool]]):
        self._path = path
        self._preprocessors = preprocessors
        self._filters = filters

    @abstractmethod
    def _process_query(self, query: Query):
        pass

    @abstractmethod
    def _results(self) -> List[int]:
        pass

    def _collect_data(self) -> None:
        with open(self._path, 'r') as file:
            for line in file:
                line = line.strip()
                try:
                    query = Query.deserialize(line)
                except ValueError:
                    continue
                for preprocess in self._preprocessors:
                    preprocess(query)
                if all(requirement(query) for requirement in self._filters):
                    self._process_query(query)

    @lru_cache
    def get(self) -> List[int]:
        self._collect_data()
        return self._results()


class TopUrlsStatistic(LogStatistic):
    __slots__ = '_freq'

    def __init__(self,
                 path: str,
                 preprocessors: List[Callable[[Query], None]],
                 filters: List[Callable[[Query], bool]]):
        super().__init__(path, preprocessors, filters)
        self._freq: Dict[str, int] = defaultdict(lambda: 0)

    def _process_query(self, query: Query):
        self._freq[query.url] += 1

    def _results(self) -> List[int]:
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
        super().__init__(path, preprocessors, filters)
        self._wait_freq: Dict[str, Tuple[int, ...]] = \
            defaultdict(lambda: tuple([0, 0]))

    def _process_query(self, query: Query):
        wait, freq = self._wait_freq[query.url]
        wait += query.response_time
        freq += 1
        self._wait_freq[query.url] = wait, freq

    def _results(self) -> List[int]:
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
    return '.' not in query.request.path.segments[-1]


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
    query.request.netloc = query.request.netloc.removeprefix('www.')


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
    return statistic(_LOG_PATH, preprocessors, filters).get()

