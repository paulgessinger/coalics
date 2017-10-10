from .broker import broker

@broker.task
def update():
    print("UPDATE2")

