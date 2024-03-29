import os

#  PQ_PW=os.environ.get("POSTGRES_PASSWORD")
#  PQ_USER=os.environ.get("POSTGRES_USER")
#  PQ_DB=os.environ.get("POSTGRES_DB")

SESSION_TABLE = "sessions"

#  SQLALCHEMY_DATABASE_URI = 'postgresql+pygresql://'+PQ_USER+':'+PQ_PW+'@db/'+PQ_DB
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]


CSRF_SECRET_KEY = os.environ["COALICS_CSRF_KEY"].encode("utf-8")
SECRET_KEY = os.environ["SECRET_KEY"]
SQLALCHEMY_TRACK_MODIFICATIONS = False

APP_PORT = os.environ.get("COALICS_APP_PORT", os.environ.get("PORT", 8080))

SOURCE_UPDATE_FREQUENCY = 30 * 60
REGEX_TIMEOUT = 10
UPDATE_PING_URL = os.environ.get("UPDATE_PING_URL", None)

REGISTER_ENABLED = os.environ.get("REGISTER_ENABLED", "False") == "True"


UPDATE_PUSHGATEWAY = os.environ.get("UPDATE_PUSHGATEWAY")


PROM_USERNAME = os.environ.get("PROM_USERNAME")
PROM_PWHASH = os.environ.get("PROM_PWHASH")
