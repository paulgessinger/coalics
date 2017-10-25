from flask import abort
from datetime import datetime
import time
import re
import bcrypt
import math
import time
import signal
from contextlib import contextmanager

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

            

def event_acceptor(source, to=10):
    posreg = re.compile(source.positive_pattern)
    negreg = re.compile(source.negative_pattern)

    # print()
    # print(source.positive_pattern, source.negative_pattern)
    # print(posreg, negreg)

    def accept_event(event):
        summary = event.summary
        # print("summary", summary)
        with timeout(to):
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

def string_shorten(string, max_length, repl="(…)"):
    if type(string) != str:
        string = str(string)
    if len(string) <= max_length+len(repl):
        return string
    
    length = len(string)
    repll = len(repl)

    a = string[0:int(math.floor(max_length/2)) - int(math.ceil(repll/2))]
    b = string[-int(math.ceil(max_length/2)) + int(math.floor(repll/2)):]

    return a + repl + b
 


class TimeoutException(Exception): pass

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutException(self.error_message)
    def __enter__(self):

        if not app.debug:
            # does not work in debug
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        if not app.debug:
            signal.alarm(0)
 
