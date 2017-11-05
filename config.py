# SQLALCHEMY_DATABASE_URI = 'sqlite:////data/test.db'

# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres@db/postgres?client_encoding=UNICODE'
SQLALCHEMY_DATABASE_URI = 'postgresql+pygresql://postgres@db/postgres'
# SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:example@db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
# SQLALCHEMY_ECHO = True
CSRF_SECRET_KEY = b'0694d5d1-87b4-4afa-b6bc-03f935f41c48'

REGEX_TIMEOUT = 2
    
REDIS_HOST='redis'
REDIS_PORT=6379

SOURCE_UPDATE_FREQUENCY = 30*60
