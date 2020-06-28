from flask import Flask, render_template, request, redirect, url_for, abort
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_session import SqlAlchemySessionInterface
import uuid
from functools import wraps
import logging
import logging.handlers
import os
from dotenv import load_dotenv

import pytz
from tzlocal import get_localzone
from flask.logging import default_handler
import platform 

#  dotenv_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env") 
#  if os.path.exists(dotenv_file):
    #  load_dotenv(dotenv_file)

app = Flask(__name__)
app.config.from_object("config")
if os.environ.get("COALICS_CONFIG"):
    app.config.from_envvar('COALICS_CONFIG')


class HostnameFilter(logging.Filter):
    hostname = platform.node()

    def filter(self, record):
        record.hostname = HostnameFilter.hostname
        return True

from logging.config import dictConfig
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(name)s/%(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

if app.debug:
  logging.getLogger().setLevel(logging.DEBUG)


# logging.getLogger("werkzeug").setLevel(logging.WARNING)

#  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


#  if not app.debug:
    #  stream_handler = logging.StreamHandler()
    #  stream_handler.setLevel(logging.INFO)
    #  app.logger.addHandler(stream_handler)

def datetimefilter(value, format='%d.%m.%Y %H:%M:%S'):
    # this will have to come from the user sometime
    tz = pytz.timezone("Europe/Zurich")
    dt = value
    local_dt = dt.astimezone(tz)
    return local_dt.strftime(format)

app.jinja_env.filters['localdate'] = datetimefilter

db = SQLAlchemy(app)

app.session_interface = SqlAlchemySessionInterface(app, db, app.config["SESSION_TABLE"], key_prefix="coalics")



from .models import User, Calendar, CalendarSource
from .forms import CalendarForm, CalendarSourceForm, DeleteForm, LoginForm, LogoutForm, EditForm
from .util import string_shorten

app.jinja_env.filters['shorten'] = string_shorten

lm = LoginManager()
lm.login_view = "login"
lm.init_app(app)


@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)


import coalics.views
