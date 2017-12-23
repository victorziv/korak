import time
import multiprocessing
from infinilab_api import Infinilab
from config import tasklogger as logger

from ..utils import (  # noqa
    assign_card_locations,
    check_hwstatus,
    collect_general_info,
    collect_vpd_info,
    detect_hba_adapters,
    enable_fcports,
    fetch_transceiver_data,
    get_nodes,
    get_server_type,
    node_is_in_dr_state,
    put_node_into_dr_state,
    put_node_into_ibox_state,
    restart_ibox_services,
    run_qaucli_command,
    system_is_up,
    validate_sw_installed,
)

infinilab = Infinilab()
from .node_adapter_worker import AdapterWorker  # noqa

# ==============================


class NodeWorker:
    def __init__(self, params):
        self.params = params
    # ________________________________________

    def __call__(self, node, queue_done):
        self.node = self.params['node'] = node
        self.queue_done = queue_done
        logger.debug("Processing node: {}".format(self.node['name']))
        self.run_tests_on_single_node()
    # ________________________________________

    def collect_info_on_hba_adapters(self):
        """Detects HBA adapters on the node, collects all the necessary info for found adapters

        - Detect HBA adapters and collect WWPN for further diagnostic
        - Assign card locations to the adapters
        - Collect VPD info per adapter

        Raises:
            Abort with assertion if no HBA adapters were detected on the node
        """
        node_hostname = self.node['name']
        logger.info("Detecting FC adapters on {0}".format(node_hostname))
        hba_adapters = detect_hba_adapters(node_hostname)

        if not len(hba_adapters):
            errmsg = 'No HBA adapters were detected on node {} - aborting'.format(node_hostname)
            logger.error(errmsg)
            assert False

        logger.info('{}: {} HBA adapters were detected'.format(node_hostname, len(hba_adapters)))

        hba_adapters = assign_card_locations(self.node, hba_adapters, self.params)
        logger.debug("{}: HBA adapters after assigning card locations: {}".format(node_hostname, hba_adapters))
        hba_adapters = collect_general_info(self.node, hba_adapters)
        hba_adapters = collect_vpd_info(self.node, hba_adapters)
        hba_adapters = self.collect_sfp_info(hba_adapters)

        return hba_adapters
    # __________________________________________

    def collect_sfp_info(self, adapters):
        for adapter in adapters:
            for port in adapter['ports']:
                port['sfp'] = fetch_transceiver_data(self.node['name'], port['wwpn'])
        return adapters
    # __________________________________________

    def run_loopback_test(self, step_name, adapter, loopback_type):

        """STEP: QLogic HBA adapter loopback test.

        Can be run only on ports that have the physical loopback circuit installed.

        Example of data_patterns included:
            '    00', '    55', '    5A', '    A5', '    AA', '    FF', 'random', ' crpat', ' cspat', 'cjtpat'

        Example of data sizes:
            Data sizes tested (bits ?): 8, 16, 32, 64, 128, 256, 512, 1024, 2048

        Test count:  number of times each diagnostic test is run. Default is 1024.

        Returns:
            list: list of dictionaries, where every dictionary is a step result.
                  Result dictionary contains:

                  `code`
                  {
                    name: bla
                    description: bla, bla, bla
                    state: finished
                    status: True
                    result_info:
                        Diagnostics Settings
                        --------------------
                        Diagnostic Mode          : Loopback
                        Data Pattern             : 00-00-00-00-00-00-00-00
                        Data Size (Bytes)        : 8
                        Number of tests (1-65535): 1024
                        Test Increment(1-65535)  : 1
                        Abort On Error           : Stop
                        Test Continuous          : OFF
                        Loopback Type            : External Loopback

                        Diagnostics - Loopback Test Result
                        ----------------------------------
                        HBA Test Data Pattern          Status    CRC       Disparity FrameLength
                        --- -----------------------  ----------- --------- --------- -----------
                         0  00-00-00-00-00-00-00-00    Success         0         0           0
                  }
        """

        node_hostname = self.node['name']
        adapter_name = '%s-%s' % (adapter['model'], adapter['sn'])

        logger.info("STEP: {} {}: Running loopback test on HBA adapter {}".format(
            node_hostname, step_name, adapter_name), extra={'color': 'blue'})

        test_params = self.params['loopback_test'][self.params['test_length']]
        data_patterns = test_params['data_patterns']
        data_sizes = test_params['data_sizes']
        test_count = test_params['test_count']

        result = {'name': step_name}
        start = time.time()

        port_statuses = []
        for port in adapter['ports']:
            wwpn = port['wwpn']

            # Loopback test will be running only on ports with physical loopback circuit
            if port['connection_mode'] != 'loop':
                continue

            for data_size in sorted(data_sizes):
                for data_pattern in data_patterns:

                    params = '-pr fc -kl %s DataSize %s LoopbackType %s DataPattern %s OnError 1 TestCount %s -x' % (
                        wwpn, data_size, loopback_type, data_pattern, test_count)

                    logger.info("Loopback test params: {}".format(params))
                    output = run_qaucli_command(node_hostname, params)
                    logger.debug("Loopback test output: {}".format(output))

                    port_statuses.append(self.validate_loopback_diagnostics(output))

        finish = time.time()
        logger.info("{} elapsed time in seconds: {:.1f}".format(step_name, finish - start))
        status = all(port_statuses)
        result.update({'status': status})
        if status:
            logger.info("{} {}: {} passed".format(node_hostname, adapter_name, step_name), extra={'color': 'green'})
        else:
            logger.error("{} {}: {} failed".format(node_hostname, adapter_name, step_name), extra={'color': 'red'})

        return result
    # ______________________________________________

    def put_node_into_infinilab_maintenance_mode(self):
        number_of_tries = 3
        repeat_counter = 0
        while True:
            try:
                repeat_counter += 1
                logger.info("%s: Entering Infinilab maintenance mode - try %s", self.node['name'], repeat_counter)
                infinilab.enter_maintenance_mode(self.params['system_name'], [self.node['location']])
                break
            except Exception:
                logger.exception("!ERROR")
                if repeat_counter <= 3:
                    logger.warning("Try %s failed - going for another shot", repeat_counter)
                    time.sleep(10)
                else:
                    logger.error("%s exceeded - giving up", number_of_tries)
                    raise

    # ______________________________________________

    def run_tests_on_single_node(self):
        try:
            if not node_is_in_dr_state(node_hostname=self.node['name'], params=self.params):
                self.put_node_into_infinilab_maintenance_mode()
                put_node_into_dr_state(node_hostname=self.node['name'], params=self.params)

            self.setup_node(self.node)
            adapters = self.collect_info_on_hba_adapters()

            # Trigger FC adapters testing
            self.test_adapters(adapters)

        except Exception:
            logger.exception("!!NODE WORKER EXCEPTION")

        finally:
            try:
                if self.params['cleanup']:
                    infinilab.exit_maintenance_mode(self.params['system_name'], [self.node['location']])
                    put_node_into_ibox_state(node_hostname=self.node['name'], params=self.params)
            except Exception:
                logger.exception("!!NODE WORKER EXCEPTION IN FINALLY BLOCK")
    # __________________________________________

    def setup_node(self, node):
        logger.info("STEP: Checking if necessary SW installed on the node {}".format(
            node['name']), extra={'color': 'blue'})
        node['server_type'] = get_server_type(node)
        logger.debug("Server type detected: {}".format(node['server_type']))
        assert validate_sw_installed(node, self.params)
    # __________________________________________

    def spawn_adapter_workers(self, adapters):
        procs = []

        for adapter in adapters:
            worker = AdapterWorker(params=self.params)
            p = multiprocessing.Process(target=worker, args=(), kwargs={
                'node': self.node,
                'adapter': adapter,
                'queue_done': self.queue_done
            })
            p.daemon = False
            p.start()
            logger.debug("Node {} adapter {} worker runs in sub-process: {}".format(
                self.node['name'], adapter['sn'], p.pid))
            procs.append(p)

        return procs
    # __________________________________________

    def test_adapters(self, adapters):

        worker_procs = self.spawn_adapter_workers(adapters)

        logger.debug("Node %s adapter procs: %r", self.node['name'], [p.pid for p in worker_procs])
        while len(worker_procs):
            for p in worker_procs:
                p.join(1)
                if not p.is_alive():
                    logger.debug("Adapter worker %s is out" % p.pid)
                    worker_procs.remove(p)

        logger.debug("Manager: All node %s adapters are done, finishing...", self.node['name'])

    # ========================================
