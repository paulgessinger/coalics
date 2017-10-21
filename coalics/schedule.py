# from coalics import app
from coalics import tasks, q, redis
from datetime import datetime

from rq_scheduler import Scheduler
from datetime import datetime

scheduler = Scheduler(connection=redis)

# scheduler.cron(
    # ,                # A cron string (e.g. "0 0 * * 0")
    # func=func,                  # Function to be queued
    # args=[arg1, arg2],          # Arguments passed into function when executed
    # kwargs={'foo': 'bar'},      # Keyword arguments passed into function when executed
    # repeat=10                   # Repeat this number of times (None means repeat forever)
    # queue_name=queue_name       # In which queue the job should be put in
# )


# scheduler.schedule(
    # scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
    # func=tasks.update_sources,                     # Function to be queued
    # args=[],             # Arguments passed into function when executed
    # kwargs={},         # Keyword arguments passed into function when executed
    # interval=10,                   # Time before the function is called again, in seconds
    # repeat=None                      # Repeat this number of times (None means repeat forever)
# )
