FROM python:3.8
MAINTAINER Paul Gessinger <hello@paulgessinger.com>

RUN pip install --no-cache-dir poetry

COPY src src
COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install

COPY . .
