FROM python:3.8-slim-buster
MAINTAINER Paul Gessinger <hello@paulgessinger.com>

RUN pip install gunicorn

ENV APP_PATH /app
WORKDIR $APP_PATH

COPY . /app
RUN pip install .




# COPY pyproject.toml .
# COPY poetry.lock .
# RUN pip install .
# RUN pip install uwsgi

# # RUN mkdir $APP_PATH/log && chown -R root:root $APP_PATH/log

# COPY src src
# COPY wsgi.py .
# COPY wait-for-it.sh .
# COPY Procfile .
# COPY migrations migrations
# COPY CHECKS .

# CMD ["python", "run.py"]
