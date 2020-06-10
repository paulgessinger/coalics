web: uwsgi --http :$PORT --wsgi-file wsgi.py --logto /dev/null
worker: python coalics/schedule.py
release: python manage.py db upgrade --directory migrations
