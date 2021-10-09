from flask import Flask, render_template, request, redirect, url_for, abort
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    current_user,
    logout_user,
)
from flask_session import SqlAlchemySessionInterface
from flask.cli import AppGroup
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


from logging.config import dictConfig

from coalics.models import db, User
from coalics.views import init_views
from coalics.util import string_shorten
from coalics.cli import init_cli


def create_app():
    app = Flask(__name__)

    app.config.from_object("coalics.config")

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(name)s/%(module)s: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {"class": "logging.StreamHandler", "formatter": "default"}
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )

    if app.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    def datetimefilter(value, format="%d.%m.%Y %H:%M:%S"):
        # this will have to come from the user sometime
        tz = pytz.timezone("Europe/Zurich")
        dt = value
        local_dt = dt.astimezone(tz)
        return local_dt.strftime(format)

    app.jinja_env.filters["localdate"] = datetimefilter

    db.init_app(app)
    Migrate(app, db)

    init_cli(app)

    app.jinja_env.filters["shorten"] = string_shorten

    lm = LoginManager()
    lm.login_view = "login"
    lm.login_message = None
    lm.init_app(app)

    @lm.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    init_views(app)

    return app
