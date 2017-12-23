import os
import time
import queue
import importlib
import datetime
from multiprocessing import Process
from lib.helpers import generate_uid
from config import logger
# from config import clean_tasklogger, set_tasklogger, get_taskconf
from config import get_taskconf
# ===============================================================


class Worker:
    def __init__(self, workerind):
        self.workerind = workerind
    # _____________________________________

    def __call__(self, queue_work, queue_sink, queue_mng):

        self.pid = os.getpid()
        logger.info("INIT WORKER in sub-proc %d", self.pid)

        while True:
            try:
                task = queue_work.get()
                task['worker'] = 'worker-%s' % self.workerind
                logger.debug("Worker-%s got task: %r", self.workerind, task)

                task['taskuid'] = '%s-%s' % (task['taskname'], generate_uid())
#                 clean_tasklogger()
#                 set_tasklogger(sessionuid=task['sessionuid'], taskuid=task['taskuid'], taskname=task['taskname'])

                task_proc = self.run_task(task, queue_sink)

                while True:

                    time.sleep(1)

                    if not task_proc.is_alive():
                        break

                    try:
                        mng = queue_mng.get_nowait()
                        logger.debug("Got MNG: %r", mng)
                        if mng['action'].lower() == 'stop':
                            task_proc.terminate()
                    except queue.Empty:
                        pass

                task_proc.join()
#                 clean_tasklogger()

            except Exception as e:
                logger.exception("!ERROR")
#                 clean_tasklogger()
                task['result'] = False
                task['state'] = 'aborted'
                task['finish'] = datetime.datetime.utcnow()
                task['message'] = str(e)
                queue_sink.put(task)
    # _____________________________________

    def compose_task_params(self, task):
        params = get_taskconf(task['taskname'])
        params.update(task)

        # Last update should be with custom task params ( get_taskconf brings in the defaults)
#         params.update(taskmodel.fetch_task_params(task['sessionuid']))

        return params
    # _____________________________________

    def run_task(self, task, queue_sink):
        taskname = task['taskname']
        taskmod = importlib.import_module('srv.task.%s.%s' % (taskname, taskname))
        taskcls = getattr(taskmod, taskname.capitalize())

        params = self.compose_task_params(task)
        taskobj = taskcls(task, params, queue_sink)
        p = Process(target=taskobj)
        p.daemon = False
        p.start()
        logger.info("Task module %s runs in sub-process: %d", taskmod.__name__, p.pid)
        return p
    # _____________________________________
