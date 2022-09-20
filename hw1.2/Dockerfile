FROM python:3.9-slim-buster as builder

WORKDIR app

COPY golf.py requirements.txt ./
COPY tests/ ./tests/

RUN python3.9 -m venv env
RUN env/bin/pip install -Ur requirements.txt

CMD ["env/bin/pytest", "--cov"]