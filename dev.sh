#!/bin/bash
flask run -h 0.0.0.0 -p 8080 &
#huey_consumer.py app.huey
celery -A app.celery worker &
celery -A app.celery beat --pidfile="/tmp/celerybeat.pid" 
