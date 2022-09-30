import os

from faker import Faker
from tempfile import NamedTemporaryFile
from datetime import datetime
from log_parse import parse, parse_date


LOGS_AMOUNT = 10000


def test_big_log():
    file = NamedTemporaryFile(mode='r+', encoding='utf-8')
    fake = Faker()
    with open(file.name, 'w'):
        top_url = 'https://sys.mail.ru/'
        start_at, stop_at = map(lambda dt:
                                datetime.strftime(dt, parse_date.DATE_FORMAT),
                                sorted([fake.date_time(), fake.date_time()]))
        top_method = 'GET'
        max_response_time = 100000

        request_date_fmt = start_at
        request_type = top_method
        request = top_url
        protocol = 'HTTP/1.1'
        response_code = 200
        response_time_str = max_response_time
        line = '[{}] "{} {} {}" {} {}'.format(
            request_date_fmt,
            request_type,
            request,
            protocol,
            response_code,
            response_time_str
        )
        file.write(line + '\n')

        for _ in range(LOGS_AMOUNT - 1):
            request_date = fake.date_time()
            request_date_fmt = datetime.strftime(request_date,
                                             parse_date.DATE_FORMAT)
            request_type = fake.http_method()
            while True:
                request = fake.uri()
                if request != top_url:
                    break
            protocol = 'HTTP/1.1'
            response_code = 200
            response_time_str = fake.random_int(0, max_response_time - 1)
            line = '[{}] "{} {} {}" {} {}'.format(
                request_date_fmt,
                request_type,
                request,
                protocol,
                response_code,
                response_time_str
            )
            file.write(line + '\n')

    os.environ['LOG_PATH'] = file.name
    assert parse(ignore_files=True, ignore_www=True,
                 start_at=start_at, stop_at=stop_at,
                 ignore_urls=['mock.mock'], slow_queries=True)[0] \
           == max_response_time
    del os.environ['LOG_PATH']
