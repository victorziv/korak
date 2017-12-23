import time
# import copy
import queue
from config import logger
# ===========================


class Sink(object):

    def set_model(self):
        from config import conf  # noqa
        from trackivt import connectdb  # noqa
        db = connectdb(conf)

        from models import Taskhandler  # noqa
        self.taskhandlermod = Taskhandler(db)
    # ________________________________________

    def __call__(self, queue_sink):

        self.set_model()

        while True:
            time.sleep(1)
            try:
                task = queue_sink.get_nowait()
                if type(task).__name__ == 'str' and task.upper() == 'QUIT':
                    logger.debug("Sink: Got QUIT, as quitting")
                    break

                if task is None:
                    continue

                logger.info("SINK: got task: %r", task)
                try:
                    taskid = task.pop('sessiontaskid')
                    logger.info("SINK: composed task with ID %s: %r", taskid, task)
                    if task['state'] == 'running':
                        self.taskhandlermod.register_worker(task)
                        self.taskhandlermod.update_session_task(taskid, task)
                    else:
                        self.taskhandlermod.update_session_task(taskid, task)
                        self.taskhandlermod.remove_from_queue(task)
                except KeyError:
                    logger.warning("TASK %r not arrived to queue", task)

            except queue.Empty:
                continue

            except Exception as e:
                logger.exception("!Exception")
                raise
    # _______________________________
