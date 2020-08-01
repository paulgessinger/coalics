import logging


from coalics import tasks, create_app

from datetime import timedelta
import time


logger = logging.getLogger("schedule")

app = create_app()

prev_job = None
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
