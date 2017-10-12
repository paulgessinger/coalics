FROM python:3
MAINTAINER Paul Gessinger <hello@paulgessinger.com>

EXPOSE 8080

ENV APP_PATH /app
WORKDIR $APP_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . . 

CMD circusd circus.ini
