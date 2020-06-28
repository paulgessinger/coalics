FROM python:3.8
MAINTAINER Paul Gessinger <hello@paulgessinger.com>

ENV APP_PATH /app
ENV PYTHONPATH /app
WORKDIR $APP_PATH

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install uwsgi

# RUN mkdir $APP_PATH/log && chown -R root:root $APP_PATH/log

COPY coalics coalics
COPY config.py .
COPY wsgi.py .
COPY wait-for-it.sh .
COPY Procfile .
COPY manage.py .
COPY migrations migrations
COPY CHECKS .

# CMD ["python", "run.py"]
