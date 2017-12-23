import os
import time
import json
import pprint
import multiprocessing

from lib.decorators import task
from srv.lib.basetask import Basetask

from .utils import (  # noqa
    activate_system,
    check_hwstatus,
    enable_fcports,
    get_nodes,
    get_enabled_ports_with_loopback,
    restart_ibox_services,
    system_is_up,
)

from .workers.node_worker import NodeWorker  # noqa
from .workers.sink import Sink  # noqa
# =====================================


# ================================


class Fcloopback(Basetask):

    @task
    def __call__(self):
        """Tests QLogic card functionality while loopbacks are installed on the FC ports.

        .. note:: A dedicated |fcloopback_script| by |sachin_more| is aimed to run similar checks in "offline" mode.

                  The |fcloopback_script_wiki| can be referred for getting the script insights.

        Following is the steps description:

        #. Check FC ports link state. Make sure only the ports with installed loopback will be tested (fc_links())
        #. Put the system in D&R state. (ibox.PutInDR())
        #. Apply a number of settings to every node on the system (SetupNode)
        #. Run a number of actual tests on the node QLogic card ( CheckNode )
            - TBD
        #. check QLogic card revision

        After all checks are done regular system state should be restored.

        :Before:
            - Enables not connected to the switch FC ports that were disabled during the before-session-start hook run.
              It is necessary due to FC Loopback test can be valid for enabled FC ports only.
              Doing it here will allow to run the FC Loopback test along with the others in a test suite in any order.

        :After:
            - Disables loopback FC ports again.
              This action removes the need to execute the test as the last one in the suite.

        :Args:
            fxsystem (object): Pre-configured Infinibox object for system-under-test.

        :Attributes:
            - name: |test_fcloopback|
            - group: ibox_system
            - ticket: |ticket_578|.
            - author: vziv@infinidat.com
            - owner: vziv@infinidat.com
            - created: 2017-05-21

            .. |ticket_578| raw:: html

                <a href="https://jira.infinidat.com/browse/IVTS-578" target="_blank">IVTS-578</a>

            .. |test_fcloopback| raw:: html

                <a
                href="https://git.infinidat.com/ivt/ivt-tests/blob/develop/tests/ibox_system/test_fcloopback.py"
                target="_blank">test_fcloopback ( Temp. link to develop branch )
                </a>

            .. |fcloopback_script| raw:: html

                <a
                href="https://git.infinidat.com/ivt/ivt-tests/blob/master/tools/FCLoopback/FCloopback.py"
                target="_blank">script
                </a>

            .. |fcloopback_script_wiki| raw:: html

                <a
                href="https://wiki.infinidat.com/display/MNFC/Fibre+Channel+Loopback+Testing"
                target="_blank">wiki article
                </a>

            .. |sachin_more| raw:: html

                <a
                href="http://infinibook/view/smore@infinidat.com/"
                target="_blank">Sachin More
                </a>
        """

        try:

            self.logger.info("===== Starting to run with params: %r", self.params)
            self.result = {}
#             self.task['start'] = datetime.datetime.utcnow()

            if self.params['system_up_check']:
                assert self.check_system_is_up(), "System is not in proper state - aborting"
                assert self.check_loopback_ports_state(), "Loopback ports state failure"

                # run HW status. If fails - warn.
                if self.params['run_hwstatus']:
                    self.check_system_hwstatus()

            # fetch nodes from infinilab
            nodes = get_nodes(self.params['system_name'], self.params['nodes_filter'])

            # Put the nodes in D&R state, test HBA adapters and boot the nodes back into IBox state
            self.run_tests(nodes)
            self.result.update(self.update_result_data())
            self.logger.info("===== Finished to run")
        except AssertionError:
            self.logger.exception("!!! TEST ASSERTION FAILURE")
            self.result.update(self.update_result_data())
            raise

        finally:

            if self.params['cleanup']:
                services_started = restart_ibox_services(
                    ibox=self.params['system_name'],
                    timeout=self.params['timeout_services_start'],
                )

                if services_started:
                    activate_system(ibox=self.params['system_name'], timeout=self.params['timeout_services_start'])
    # __________________________________________
    # ____________________________________

    def before(self):

        self.logger.infoblue("==> Before")

        # FC loopback test can be executed on enabled ports only.
        enable_fcports()
    # ____________________________________

    def check_loopback_ports_state(self):
        self.logger.info('STEP: Checking all loopback ports have link', extra={'color': 'blue'})
        found_loopback_ports = get_enabled_ports_with_loopback(self.params['system_name'])
        self.logger.info("Found loopback ports: %r", found_loopback_ports)
        diff = list(set(self.params['loopback_ports']).difference(set(found_loopback_ports)))
        if len(diff):
            self.logger.error(
                "!ERROR: Following loopback FC ports do not have a link: {}".format(diff), extra={'color': 'red'}
            )
            return False

        self.logger.info("All required FC loopback ports are enabled and have link", extra={'color': 'green'})
        return True
    # ____________________________________

    def check_system_is_up(self):
        self.logger.info('STEP: Checking the system {} is UP ( ACTIVE or STANDBY )'.format(
            self.params['system_name']), extra={'color': 'blue'})

        system_up = system_is_up(self.params['system_name'])
        if system_up:
            self.logger.info("The system found in ACTIVE state", extra={'color': 'green'})
            return True
        else:
            self.logger.error(
                "System {} is not ready for proceeding. Bring it UP and re-run the test".format(
                    self.params['system_name']), extra={'color': 'red'})
            return False
    # ____________________________________

    def check_system_hwstatus(self):

        self.logger.info('STEP: Run hwstatus.sh on the Infinibox system {}'.format(
            self.params['system_name']), extra={'color': 'blue'})

        hwstatus = check_hwstatus(self.params['system_name'])
        if hwstatus:
            self.logger.info("HW Status is OK", extra={'color': 'green'})
            return True
        else:
            self.logger.warning("HW Status reported errors", extra={'color': 'yellow'})
            return False
    # ____________________________________

    def update_result_data(self):
        result_file = os.path.join(os.path.dirname(self.logger.pathinfo), '%s.json' % self.params['taskname'])

        try:
            with open(result_file) as fp:
                nodes_result = json.load(fp)
        except FileNotFoundError:
            self.logger.exception("!!! PROBLEM WITH RESULTS FILE?")
            nodes_result = {}
            self.result['result'] = False
        else:
            self.logger.info("Node results fetched from SINK: {}".format(nodes_result))
            self.result['nodes'] = nodes_result
            self.result['result'] = all([step['status'] for node in self.result['nodes'] for step in node['steps']])

        self.logger.info('FINAL RESULT: {}'.format(pprint.pformat(self.result)))
        return self.result
    # __________________________________________

    def get_result(self):
        self.logger.info("Getting task result")
        return self.result
    # __________________________________________

    def run_tests(self, nodes):

        node_worker_procs = []
        queue_done = multiprocessing.Queue()
        self.logger.info("=====> PARAMS: %r", self.params)
        node_worker_procs.extend(self.spawn_node_workers(nodes=nodes, queue_done=queue_done))
        sink_proc = self.spawn_sink(queue_done)

        self.logger.debug("Node worker procs: %r" % [p.pid for p in node_worker_procs])
        while len(node_worker_procs):
            for p in node_worker_procs:
                p.join(1)
                if not p.is_alive():
                    self.logger.debug("Manager: Node worker %s is out" % p.pid)
                    node_worker_procs.remove(p)

        queue_done.put('QUIT')
        while sink_proc.is_alive():
            self.logger.debug("Sink {} is still UP".format(sink_proc))
            time.sleep(1)

        self.logger.debug("Manager: All node workers are done, finishing...")
    # _______________________________

    def spawn_node_workers(self, nodes, queue_done):

        procs = []

        for node in nodes:
            worker = NodeWorker(params=self.params)
            p = multiprocessing.Process(target=worker, args=(), kwargs={'node': node, 'queue_done': queue_done})
            p.daemon = False
            p.start()
            self.logger.debug("Node worker {} runs in sub-process: {}".format(node['name'], p.pid))
            procs.append(p)

        return procs
    # _______________________________

    def spawn_sink(self, queue_done):

        sink = Sink(params=self.params)
        p = multiprocessing.Process(target=sink, args=(), kwargs={'queue_done': queue_done})
        p.daemon = True
        p.start()
        self.logger.debug("Sink runs in sub-process: %d" % p.pid)
        return p

        # ========================================
