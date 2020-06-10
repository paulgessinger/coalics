web: uwsgi --http :$PORT --wsgi-file wsgi.py
worker: python coalics/schedule.py
release: python manage.py db upgrade --directory migrations
