from flask import abort
from datetime import datetime
import time
import re

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

            

def event_acceptor(source):
    posreg = re.compile(source.positive_pattern)
    negreg = re.compile(source.negative_pattern)

    # print()
    # print(source.positive_pattern, source.negative_pattern)
    # print(posreg, negreg)

    def accept_event(event):
        summary = event.summary
        # print("summary", summary)
        posmatch = posreg.match(summary)
        # print("pos", posmatch)
        if len(source.negative_pattern) == 0:
            return posmatch != None
        else:
            negmatch = negreg.match(summary)
            # print("neg", negmatch)
            return posmatch != None and negmatch == None
    return accept_event
