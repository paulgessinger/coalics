from datetime import timedelta
import time

from flask.cli import AppGroup
from flask import current_app

from coalics.models import db
from coalics import tasks


def init_cli(app):

    cli = AppGroup("coalics")

    @cli.command("init_db")
    def init_db():
        db.create_all()

    @cli.command("schedule")
    def schedule():
        logger = current_app.logger
        td = timedelta(seconds=app.config["SOURCE_UPDATE_FREQUENCY"])
        logger.info("Scheduler launching")
        while True:
            try:
                logger.info("Begin schedule run")
                tasks.update_sources()
                logger.info("Scheduler: ran without error")
            except Exception as e:
                logger.error("Scheduler: caught error {}".format(str(e)), exc_info=True)
            finally:
                logger.info("Scheduler: Sleeping for {}s".format(td.seconds))
                time.sleep(td.seconds)

    app.cli.add_command(cli)
