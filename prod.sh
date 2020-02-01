#!/bin/bash

date

echo "Waiting for 5s for database"
sleep 5
echo "Launching"

export COALICS_CONFIG=/app/config.prod.py

python run.py &

# for i in {1..4}; do
  # #rq worker -u "redis://redis:6379" &
  # echo "Launching worker $i"
  # rq worker -c rq_config &
  # sleep 0.5
# done

echo "Launching rq scheduler"
python coalics/schedule.py &

wait
