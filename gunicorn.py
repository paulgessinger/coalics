import os

# if os.environ.get('MODE') == 'dev':
    # reload = True
# capture_output = True

bind = '0.0.0.0:8080'

errorlog = 'log/gunicorn_error.log'
loglevel = 'info'
accesslog = 'log/gunicorn_access.log'

# errorlog = "-"
# accesslog = "-"
