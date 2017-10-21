from flask import Flask, render_template, request, redirect, url_for, abort
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_session import RedisSessionInterface
import uuid
from functools import wraps
import logging
from redis import StrictRedis
from rq import Queue

import pytz
from tzlocal import get_localzone


app = Flask(__name__)
app.config.from_object("config")

def datetimefilter(value, format='%d.%m.%Y %H:%I:%S'):
    # this will have to come from the user sometime
    tz = pytz.timezone("Europe/Zurich")
    dt = value
    local_dt = dt.astimezone(tz)
    return local_dt.strftime(format)

app.jinja_env.filters['localdate'] = datetimefilter

db = SQLAlchemy(app)

redis = StrictRedis(host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"])
app.session_interface = RedisSessionInterface(redis, __name__)

q = Queue(connection=redis)


from .models import User, Calendar, CalendarSource
from .forms import CalendarForm, CalendarSourceForm, DeleteForm, LoginForm, LogoutForm, EditForm




migrate = Migrate(app, db)

lm = LoginManager()
lm.login_view = "login"
lm.init_app(app)


@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)


import coalics.views
