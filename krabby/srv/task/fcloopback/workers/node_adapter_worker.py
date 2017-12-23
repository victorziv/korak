import sys
import multiprocessing
from infinilab_api import Infinilab
from config import tasklogger as logger

infinilab = Infinilab()
from .node_adapter_port_worker import PortWorker  # noqa

# ==============================


class AdapterWorker:
    def __init__(self, params):
        self.params = params
    # ________________________________________

    def __call__(self, node, adapter, queue_done):
        self.node = node
        self.adapter = adapter
        self.queue_done = queue_done
        logger.debug("Processing node: {}".format(self.node['name']))
        result = self.run_tests_on_adapter()
        self.queue_done.put(result)
    # ________________________________________

    def run_tests_on_adapter(self):

        try:
            worker_procs = self.spawn_port_workers()

            logger.debug("Node %s adapter %s  FC port procs: %r",
                self.node['name'], self.adapter['sn'], [p.pid for p in worker_procs])  # noqa
            while len(worker_procs):
                for p in worker_procs:
                    p.join(1)
                    if not p.is_alive():
                        logger.debug("Port worker %s is out" % p.pid)
                        worker_procs.remove(p)

            logger.debug("All node %s adapters are done, finishing...", self.node['name'])

        except Exception:
            logger.exception("!!ADAPTER EXCEPTION")
            sys.exit(1)
    # __________________________________________

    def spawn_port_workers(self):
        procs = []

        for port in self.adapter['ports']:

            if port['connection_mode'] != 'loop':
                logger.info("%s %s: No loopback on port %s - skipping",
                    self.node['name'], self.adapter['sn'], port['wwpn'])  # noqa
                continue

            worker = PortWorker(params=self.params)
            p = multiprocessing.Process(target=worker, args=(), kwargs={
                'node': self.node,
                'adapter': self.adapter,
                'port': port,
                'queue_done': self.queue_done
            })
            p.daemon = True
            p.start()
            logger.debug("Node %s adapter %s Port %s worker runs in sub-process: %s",
                self.node['name'], self.adapter['sn'], port['wwpn'], p.pid)  # noqa
            procs.append(p)

        return procs
    # __________________________________________
