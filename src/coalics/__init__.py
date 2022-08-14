from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
import logging.handlers
import os

import pytz
from prometheus_flask_exporter import PrometheusMetrics
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


from logging.config import dictConfig

from coalics import config
from coalics.models import db, User
from coalics.views import init_views
from coalics.util import string_shorten
from coalics.cli import init_cli


def create_app():
    app = Flask(__name__)

    basic_auth = HTTPBasicAuth()

    @basic_auth.verify_password
    def verify_password(username, password):
        if config.PROM_USERNAME is None or config.PROM_PWHASH is None:
            return False
        if username != config.PROM_USERNAME:
            return False
        return check_password_hash(config.PROM_PWHASH, password)

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

    app.jinja_env.globals["git_rev"] = os.environ.get("GIT_REV")

    lm = LoginManager()
    lm.login_view = "login"
    lm.login_message = None
    lm.init_app(app)

    @lm.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    metrics = PrometheusMetrics(
        app,
        defaults_prefix="coalics",
        path="/metrics",
        metrics_decorator=basic_auth.login_required,
    )

    init_views(app, metrics)

    return app
