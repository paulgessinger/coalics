from celery import Celery
broker = Celery('tasks', broker='redis://redis')
