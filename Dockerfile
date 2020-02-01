FROM python:3
MAINTAINER Paul Gessinger <hello@paulgessinger.com>

EXPOSE 8080

ENV APP_PATH /app
ENV PYTHONPATH /app
WORKDIR $APP_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir $APP_PATH/log

COPY . . 
