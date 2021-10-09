import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import logging


from coalics import tasks, app
from datetime import datetime

from datetime import datetime, timedelta
import time


#  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger("schedule")

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
