import re
from typing import List, Callable
from datetime import datetime
from furl import furl
from http import HTTPStatus


LOG_FILE_PATH = 'log.log'


class Query:
    __slots__ = ('request_date',
                 'request_type',
                 'request',
                 'protocol',
                 'response_code',
                 'response_time')

    _DATE_FORMAT = '%d/%b/%Y %H:%M:%S'
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
        self.request_date = datetime.strptime(request_date_str,
                                              self._DATE_FORMAT)
        self.request_type = request_type_str
        self.request = furl(request_str)
        self.protocol = protocol_str
        self.response_code = int(response_code_str)
        if self.response_code not in self._http_response_codes:
            raise ValueError
        self.response_time = int(response_time_str)

    @property
    def urlstr(self) -> str:
        return self.request.netloc + self.request.pathstr

    @classmethod
    def deserialize(cls, s: str) -> 'Query':
        match = cls._query_pattern.fullmatch(s)
        if not match:
            raise ValueError
        return Query(*match.groups())


def is_not_file(query: Query) -> bool:
    return '.' not in query.request.path.segments[-1]


def is_not_ignored_url(ignored_urls: List[str]) -> Callable[[Query], bool]:
    ignored_urls_set = set(ignored_urls)

    def f(query: Query) -> bool:
        return query.urlstr not in ignored_urls_set
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
    requirements: List[Callable[[Query], bool]] = []
    if ignore_files:
        requirements.append(is_not_file)
    if ignore_urls:
        requirements.append(is_not_ignored_url(ignore_urls))
    if start_at:
        requirements.append(is_after(start_at))
    if stop_at:
        requirements.append(is_before(stop_at))
    if request_type:
        requirements.append(is_request_type(request_type))

    transforms: List[Callable[[Query], None]] = []
    if ignore_www:
        transforms.append(remove_www_prefix)

    result = []
    with open(LOG_FILE_PATH, 'r') as file:
        for line in file:
            line = line.strip()
            try:
                query = Query.deserialize(line)
            except ValueError:
                continue
            for transform in transforms:
                transform(query)
            if all(requirement(query) for requirement in requirements):
                result.append(query.urlstr)
    return result

print(*parse(ignore_files=True, ignore_urls=[
    'sys.mail.ru/calendar/meeting/254/40261/'],
             ignore_www=False))

