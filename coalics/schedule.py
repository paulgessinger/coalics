import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import logging



from coalics import tasks, app
from datetime import datetime

from datetime import datetime, timedelta
import time


#  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

prev_job = None
td = timedelta(seconds=app.config["SOURCE_UPDATE_FREQUENCY"])
app.logger.info("Scheduler launching")
while True:
    try:
        app.logger.info("Begin schedule run")
        tasks.update_sources()
        app.logger.info("Scheduler: ran without error")
    except Exception as e:
        app.logger.error("Scheduler: caught error {}".format(str(e)), exc_info=True)
    finally:
        app.logger.info("Scheduler: Sleeping for {}s".format(td.seconds))
        time.sleep(td.seconds)
