from functools import wraps
import datetime
from lib.exceptions import TaskStoppedException
from config import clean_tasklogger, set_tasklogger
# =================================================


def cleanup_task(self):
    task = self.task
    self.logger.info("Finishing task %s ( %s )", task['taskname'], task['taskuid'])
    clean_tasklogger(self.logger)
# ___________________________________________________


def init_task(self):
    task = self.task
    self.logger = set_tasklogger(sessionuid=task['sessionuid'], taskuid=task['taskuid'], taskname=task['taskname'])

    task['log'] = self.logger.pathinfo

    self.logger.info(
        " ====== Session: {}: Starting TASK {} ( {} ) ========".format(
            task['sessionuid'], task['taskname'], task['taskuid']))

    task['state'] = 'running'
    task['start'] = datetime.datetime.utcnow()
    self.logger.debug("Task after init: %r", task)
    return task
# ___________________________________________________


def task(target):

    def wrapper(self, *args, **kwargs):
        try:
            self.task.update(init_task(self))

            # Update task state before starting to run
            self.queue_sink.put(self.task)

            target(self, *args, **kwargs)
            result = self.get_result()
            self.task.update(result)
            self.task['state'] = 'finished'
        except TaskStoppedException:
            self.task['result'] = None
            self.task['state'] = 'finished'
        except Exception as e:
            self.logger.exception("!TASK EXCEPTION")
            self.task['state'] = 'aborted'
            self.task['message'] = str(e)
            self.task['result'] = False
        finally:
            self.task['finish'] = datetime.datetime.utcnow()
            self.task['total_elapsed_seconds'] = round((self.task['finish'] - self.task['start']).total_seconds())
            self.logger.info("TASK {}: elapsed time: {:.0f} min".format(
                self.task['taskname'], self.task['total_elapsed_seconds'] / 60))
            self.logger.debug("--------- FINISHED. PUT IN SINK: %r", self.task)
            self.queue_sink.put(self.task)
            cleanup_task(self)

    return wraps(target)(wrapper)
