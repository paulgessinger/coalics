import os
#  PQ_PW=os.environ.get("POSTGRES_PASSWORD")
#  PQ_USER=os.environ.get("POSTGRES_USER")
#  PQ_DB=os.environ.get("POSTGRES_DB")

SESSION_TABLE="sessions"

#  SQLALCHEMY_DATABASE_URI = 'postgresql+pygresql://'+PQ_USER+':'+PQ_PW+'@db/'+PQ_DB
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


CSRF_SECRET_KEY = os.environ.get("COALICS_CSRF_KEY").encode("utf-8")
SQLALCHEMY_TRACK_MODIFICATIONS = False

APP_PORT=os.environ.get("COALICS_APP_PORT", os.environ.get("PORT", 8080))

SOURCE_UPDATE_FREQUENCY = 30*60
REGEX_TIMEOUT=10
UPDATE_PING_URL=os.environ.get("UPDATE_PING_URL", None)
