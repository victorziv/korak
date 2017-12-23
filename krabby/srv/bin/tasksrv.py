#!/usr/bin/env python

import time
import datetime
import queue
from multiprocessing import Process, Queue

from config import Configurator
Configurator.configure()
Configurator.set_logging("tasksrv", console_logging=True)

from config import logger, conf  # noqa
from trackivt import connectdb  # noqa
db = connectdb(conf)

from models import Taskhandler  # noqa
taskhandlermod = Taskhandler(db)

from srv.lib.taskworker import Worker  # noqa
from srv.lib.tasksink import Sink  # noqa
# ===================================


class Tasksrv:

    def run(self):

        try:
            procs = []
            queue_work = Queue(maxsize=10)
            queue_sink = Queue(maxsize=10)
            mng_queues = {'worker-%s' % ind: Queue(maxsize=10) for ind in range(1, conf['TASK_WORKERS'] + 1)}
            procs.append(self.spawn_sink(queue_sink))
            procs.extend(self.spawn_workers(queue_work, queue_sink, mng_queues))

            while len(procs):

                time.sleep(conf['TASK_POLL_INTERVAL'])

                try:
                    mng = taskhandlermod.fetch_taskmng()
                    if mng:
                        logger.debug("Task mng: %r", mng)
                        worker = taskhandlermod.fetch_task_worker(mng['sessionuid'])
                        logger.debug("Task worker: %r", worker)
                        mngqueue = mng_queues[worker]
                        logger.info("MNG queue: %r", mngqueue)
                        mng_queues[worker].put(mng, block=True, timeout=10)
                except queue.Full:
                    logger.error("Management queue is full, mng %s will stay in queued state", mng['sessionuid'])
                    taskhandlermod.reset_taskmng_fetch(mng)
                    continue
                except KeyError:
                    logger.warning(
                        "TASK %s has been terminated before it had a chance to take action %r",
                        mng['taskname'],
                        mng.pop('action')
                    )
                    mng['worker'] = None
                    mng['result'] = None
                    mng['state'] = 'terminated'
                    mng['message'] = '%s has been terminated' % mng['taskname']
                    mng['finish'] = datetime.datetime.utcnow()
                    queue_sink.put(mng)
                except Exception:
                    logger.exception("!Queue EXCEPTION")
                    continue

                try:
                    task = taskhandlermod.fetch_queued_task()
                    if task:
                        logger.info("Dispatcher FETCHED TASK FROM DB: %r", task)
                        queue_work.put(task, block=True, timeout=10)
                except queue.Full:
                    logger.error("Worker queue is full, task %s will stay in queued state", task['taskname'])
                    taskhandlermod.reset_task_fetch(task['sessionuid'])
                    continue
                except Exception:
                    logger.exception("!Queue EXCEPTION")
                    taskhandlermod.reset_task_fetch(task['sessionuid'])
                    continue

                for p in procs:
                    p.join(1)
                    if not p.is_alive():
                        logger.debug("Tasksrv: process PID %s is out" % p.pid)
                        procs.remove(p)
                        logger.debug("Procs list length: %r", len(procs))

            logger.info("Finished, going down...")

        except Exception:
            logger.exception("!Run EXCEPTION")
            raise
    # _______________________________

    def spawn_sink(self, queue_sink):
        """
        Sink should be spawned from the main tasksrv ( dispatcher ) process on the master node
        """

        sink = Sink()
        p = Process(target=sink, args=(), kwargs={'queue_sink': queue_sink})
        p.daemon = True
        p.start()
        logger.info("Sink runs in sub-process: %d", p.pid)

        return p
    # _______________________________

    def spawn_workers(self, queue_work, queue_sink, mng_queues):

        procs = []

        for ind in range(1, conf['TASK_WORKERS'] + 1):
            worker = Worker(ind)
            p = Process(
                target=worker, args=(),
                kwargs={
                    'queue_work': queue_work,
                    'queue_sink': queue_sink,
                    'queue_mng': mng_queues['worker-%s' % ind]
                })
            p.daemon = False
            p.start()
            logger.info("Worker %d runs in sub-process: %d", 1, p.pid)
            procs.append(p)

        return procs
# ==================================


def main():
    srv = Tasksrv()
    srv.run()
# ==================================


if __name__ == '__main__':
    main()
