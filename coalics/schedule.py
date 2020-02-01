import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import logging

from coalics import tasks, q, redis, app
from datetime import datetime

from datetime import datetime, timedelta
import time


# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.INFO)
# app.logger.addHandler(stream_handler)
logger = logging.getLogger("Scheduler")
# os.system("ls -al /app")
# os.system("ls -al /app/log")
# fh = logging.FileHandler("/app/log/scheduler.log")
# fh.setLevel(logging.INFO)
#  logger.setLevel(logging.DEBUG)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
# fh.setFormatter(formatter)

# logger.addHandler(fh)

prev_job = None
td = timedelta(seconds=app.config["SOURCE_UPDATE_FREQUENCY"])
logger.info("Scheduler launching")
while True:
    try:
        logger.info("Begin schedule run")
        #  q.enqueue(tasks.update_sources, timeout=td.seconds*0.9)
        tasks.update_sources()
        logger.info("Scheduler: ran without error")
    except Exception as e:
        logger.error("Scheduler: caught error {}".format(str(e)))
    finally:
        logger.info("Scheduler: Sleeping for {}s".format(td.seconds))
        time.sleep(td.seconds)
