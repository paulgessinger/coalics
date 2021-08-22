web: uwsgi --http :$PORT --wsgi-file wsgi.py
worker: python coalics/schedule.py
release: flask db upgrade
