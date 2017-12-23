#!/usr/bin/env python
import copy
import datetime
import time
import os
import pkgutil
from multiprocessing import Process, Queue
from config import Config
sessionid = datetime.datetime.now().strftime('%Y%m%d%H%M%S-%f')
Config.set_logging(name='testrunner', session=sessionid, console_logging=True, console_loglevel='DEBUG')

from config import logger  # noqa
from srv.lib.registry import testcase_registry  # noqa
from models import Testcase  # noqa
from pandorabox import create_app  # noqa
app = create_app(os.getenv('PANDORABOX_CONFIG') or 'default')
# =================================


class Sink:
    def __init__(self):
        pass
    # ____________________________

    def __call__(self, queue_result):
        while True:
            time.sleep(1)

# =================================


class Worker:
    def __init__(self, case):
        self.case = case
    # ____________________

    def __call__(self, queue_result):
        self.case['func']()
# =================================


def enumerate_cases():
    """
    Imports testcases and puts the active ones into testcase_registry
    """
    testcase_path = os.path.join(Config.BASEDIR, 'srv', 'testcase')
    for loader, name, is_pkg in pkgutil.walk_packages(path=[testcase_path]):
        loader.find_module(name).load_module(name)

    logger.info("Testcases registered: {}".format(testcase_registry))
    cache_enumerated_cases()
# ____________________________________________


def run():

    enumerate_cases()
    logger.debug("Registry: {}".format(testcase_registry))

    sessionid = datetime.datetime.now().strftime('%Y%m%d%H%M%S-%f')
    logger.info("Session ID: {}".format(sessionid))

    logger.info("Running all registered testcases")
    trigger_cases()

# ___________________________


def cache_enumerated_cases():
    for testcase in testcase_registry:
        tc = copy.copy(testcase)
        tc.pop('func')
        Testcase.add(tc)
# ___________________________


def start_sink(queue_result):
    sink = Sink()
    p = Process(target=sink, args=(), kwargs={'queue_result': queue_result})
    p.daemon = True
    p.start()
    logger.info("Sink starts in sub-process: {}".format(p.pid))
    return p
# ___________________________


def start_workers(queue_result):
    procs = []

    for case in testcase_registry:
        worker = Worker(case)
        p = Process(target=worker, args=(), kwargs={'queue_result': queue_result})
        p.daemon = True
        p.start()
        logger.debug("Worker for case {} runs in sub-process: {}".format(case['name'], p.pid))
        procs.append(p)

    return procs
# ___________________________


def trigger_cases():
    procs = []
    queue_result = Queue()
    procs.extend(start_workers(queue_result))
#     procs.append(start_sink(queue_result))

    while len(procs):
        for proc in procs:
            proc.join(1)
            if not proc.is_alive():
                procs.remove(proc)

    logger.info("Finished running testcases: {}".format(testcase_registry))
# ___________________________


if __name__ == '__main__':
    run()
