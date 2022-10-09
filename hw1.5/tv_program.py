import sys
import requests
from pydantic import BaseModel


API_URL = 'https://www.tvmaze.com/api#show-single-search'


if __name__ == '__main__' or __name__ == 'tv_program':
    response = requests.get(API_URL)
    print(response.content)
