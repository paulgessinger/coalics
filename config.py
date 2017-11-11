import os
PQ_PW=os.environ.get("POSTGRES_PASSWORD")
PQ_USER=os.environ.get("POSTGRES_USER")
PQ_DB=os.environ.get("POSTGRES_DB")

SQLALCHEMY_DATABASE_URI = 'postgresql+pygresql://'+PQ_USER+':'+PQ_PW+'@db/'+PQ_DB
CSRF_SECRET_KEY = os.environ.get("COALICS_CSRF_KEY").encode("utf-8")
SQLALCHEMY_TRACK_MODIFICATIONS = False

REGEX_TIMEOUT = 2
    
REDIS_HOST='redis'
REDIS_PORT=6379

SOURCE_UPDATE_FREQUENCY = 30*60
