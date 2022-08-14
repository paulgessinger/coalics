from datetime import timedelta
import time

from flask.cli import AppGroup
from flask import current_app
from prometheus_client import push_to_gateway

from coalics.models import db
from coalics import tasks, config
from coalics.metrics import push_registry, update_success_time


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

    @cli.command("update")
    def update():
        logger = current_app.logger
        logger.info("Begin update run")
        tasks.update_sources()
        logger.info("Update ran without error")

        if config.UPDATE_PUSHGATEWAY is not None:
            push_to_gateway(config.UPDATE_PUSHGATEWAY, "coalics_update", push_registry)
        update_success_time.set_to_current_time()

    app.cli.add_command(cli)
