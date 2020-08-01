import os

SESSION_TYPE = "sqlalchemy"
# SESSION_TABLE = "sessions"

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

SECRET_KEY = os.environ.get("SECRET_KEY")
CSRF_SECRET_KEY = os.environ.get("COALICS_CSRF_KEY", "blub").encode("utf-8")
SQLALCHEMY_TRACK_MODIFICATIONS = False

APP_PORT = os.environ.get("COALICS_APP_PORT", os.environ.get("PORT", 8080))

SOURCE_UPDATE_FREQUENCY = 30 * 60
REGEX_TIMEOUT = 10
UPDATE_PING_URL = os.environ.get("UPDATE_PING_URL", None)

REGISTER_ENABLED = os.environ.get("REGISTER_ENABLED", "True") == "True"
