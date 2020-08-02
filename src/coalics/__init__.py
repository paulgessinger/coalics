from coalics.util import string_shorten
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

import pytz
from logging.config import dictConfig
import logging

from .models import db, User
from .views import init_views


def create_app():
    app = Flask(__name__)
    app.config.from_object("coalics.config")

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": (
                        "[%(asctime)s] %(levelname)s in"
                        " %(name)s/%(module)s: %(message)s"
                    )
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
