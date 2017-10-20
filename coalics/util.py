from flask import abort
from datetime import datetime
import time

from coalics import app

def get_or_abort(model, object_id, code=404):
    result = model.query.get(object_id)
    if result is None:
        abort(code)
    return result

class TaskTimeout(RuntimeError):
    pass

def wait_for(tasks, timeout=None, tick=0.1):
    start = datetime.now()
    for task in tasks:
        while not task.result:
            time.sleep(tick)
            if timeout != None:
                now = datetime.now()
                delta = now - start
                if delta.seconds > timeout:
                    raise TaskTimeout()

            
