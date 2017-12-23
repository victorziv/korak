import signal
from lib.exceptions import TaskStoppedException
# =============================


def sigterm_handler(signal, frame):
    raise TaskStoppedException("TASK STOPPED")
# =============================


signal.signal(signal.SIGTERM, sigterm_handler)


class Basetask:
    def __init__(self, task, params, queue_sink):
        self.task = task
        self.params = params
        self.queue_sink = queue_sink
