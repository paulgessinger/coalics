from flask import abort
from datetime import datetime
import time
import re
import bcrypt

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
    if type(tasks) != list:
        tasks = [tasks]
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

class BcryptPassword():
    def __init__(self, **kwargs):

        if "hash" in kwargs and "password" in kwargs:
            raise ValueError("Create with either hash or pw")

        if "hash" in kwargs:
            self.hash = kwargs["hash"]
        elif "password" in kwargs:
            self.hash = bcrypt.hashpw(kwargs["password"].encode("utf-8"), bcrypt.gensalt())
        else:
            raise ValueError("Create with either hash or pw")

    def __eq__(self, test):
        return bcrypt.checkpw(test.encode("utf-8"), self.hash)

    def __neq__(self, test):
        return not self.__eq__()
