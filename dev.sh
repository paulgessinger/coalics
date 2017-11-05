#!/bin/bash
#pip install -e .
#flask run -h 0.0.0.0 -p 8080 &
python run.py &
#huey_consumer.py app.huey
#celery -A app.celery worker &
#celery -A app.celery beat --pidfile="/tmp/celerybeat.pid" 
#rq worker -c rq_config

for i in {1..4}; do
  #rq worker -u "redis://redis:6379" &
  echo "Launching worker $i"
  rq worker -c rq_config &
  sleep 0.5
done

#rq worker -u "redis://redis:6379" &


echo "Launching rq scheduler"
#rqscheduler --host redis --port 6379 &
python coalics/schedule.py &

wait
