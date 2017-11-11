import pg
from dotenv import load_dotenv
import os
import time

def check_database(*args, **kw):
    dotenv_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env") 
    load_dotenv(dotenv_file)
    PQ_PW=os.environ.get("POSTGRES_PASSWORD")
    PQ_USER=os.environ.get("POSTGRES_USER")
    PQ_DB=os.environ.get("POSTGRES_DB")

    for i in range(10):
        time.sleep(1)
        try:
            pg.connect(dbname=PQ_DB, host='db', user=PQ_USER, passwd=PQ_PW)
            return True
        except:
            # no connection
            pass

    # if we get here, all attempts have failed, let's launch anyway
    return True
