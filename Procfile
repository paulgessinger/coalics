web: gunicorn --threads 4 -b :$PORT wsgi
worker: flask coalics schedule
release: flask db upgrade
