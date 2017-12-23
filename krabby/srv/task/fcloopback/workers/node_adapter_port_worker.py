import pprint
import time
import datetime
from infinilab_api import Infinilab
from config import tasklogger as logger

from ..utils import (  # noqa
    run_qaucli_command,
)

infinilab = Infinilab()

# ==============================


class PortWorker:
    def __init__(self, params):
        self.params = params
    # ________________________________________

    def __call__(self, node, adapter, port, queue_done):
        self.node = node
        self.adapter = adapter
        self.port = port
        self.queue_done = queue_done
        logger.debug("{}: Processing node".format(self.node['name']))
        result = self.run_tests_on_port()
        logger.info("%s: Result before seding to sink: %r", self.node['name'], result)
        self.queue_done.put(result)
    # ________________________________________

    def run_loopback_test(self, step_name, loopback_type):

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
        adapter_name = '%s-%s' % (self.adapter['model'], self.adapter['sn'])

        logger.info("STEP: {} {}: Running loopback test on HBA adapter {}".format(
            node_hostname, step_name, adapter_name), extra={'color': 'blue'})

        test_params = self.params['loopback_test'][self.params['test_length']]
        data_patterns = test_params['data_patterns']
        data_sizes = test_params['data_sizes']
        test_count = test_params['test_count']

        result = {'name': step_name}
        start = time.time()

        wwpn = self.port['wwpn']

        statuses = []
        for data_size in sorted(data_sizes):
            for data_pattern in data_patterns:

                params = '-pr fc -kl %s DataSize %s LoopbackType %s DataPattern %s OnError 1 TestCount %s -x' % (
                    wwpn, data_size, loopback_type, data_pattern, test_count)

                logger.info("{}: Loopback test params: {}".format(node_hostname, params))
                output = run_qaucli_command(node_hostname, params)
                logger.debug("Loopback test output: {}".format(output))

                statuses.append(self.validate_loopback_diagnostics(output))

        finish = time.time()
        logger.info("{}: {} elapsed time in seconds: {:.1f}".format(node_hostname, step_name, finish - start))
        port_status = all(statuses)
        result.update({'status': port_status})
        if port_status:
            logger.info("Node {} Adapter {} Port {}: {} passed".format(
                node_hostname, adapter_name, wwpn, step_name), extra={'color': 'green'})
        else:
            logger.error("Node {} Adapter {} Port {}: {} failed".format(
                node_hostname, adapter_name, wwpn, step_name), extra={'color': 'red'})

        return result
    # ______________________________________________

    def run_steps(self):

        """Takes all required steps to verify and diagnose an HBA adapter FC port

        """
        results = []

        # Step 1
        results.append(self.test_hba_adapter_revision())

        # Step 2
        results.append(self.test_sfp_model())

        # Step 3
        results.append(self.test_sfp_revision())

        # Step 4: external loopback test
        results.append(self.test_external_loopback())

        # Step 5: transceiver diagnostic test
        results.append(self.test_sfp_diagnostics())

        # Step 6: 1-bit serial internal loopback test
        results.append(self.test_internal_loopback_bit1())

        logger.debug("%s Adapter %s Port %s: Total steps: %r",
                    self.node['name'], self.adapter['sn'], self.port['wwpn'], len(results))  # noqa

        logger.info("STEP RESULTS: {}".format(results))
        return results
    # ______________________________________________

    def run_tests_on_port(self):
        """
        Note: this method goes into a separate process to run
        on all detected adapters simultaneously
        """

        try:

            start = datetime.datetime.utcnow()

            # TODO Additional sub-process will be spawned to run the test sequence per HBA adapter
            step_results = self.run_steps()

            finish = datetime.datetime.utcnow()
            elapsed_seconds = round((finish - start).total_seconds())
            return {
                'sessionuid': self.params['sessionuid'],
                'taskname': self.params['taskname'],
                'node': self.node['name'],
                'adapter': self.adapter['sn'],
                'port': self.port['wwpn'],
                'steps': step_results,
                'elapsed_seconds': elapsed_seconds
            }
        except Exception:
            logger.exception("!RUN TEST ON PORT EXCEPTION")
            return {
                'sessionuid': self.params['sessionuid'],
                'taskname': self.params['taskname'],
                'node': self.node['name'],
                'adapter': self.adapter['sn'],
                'port': self.port['wwpn'],
                'steps': [],
                'elapsed_seconds': elapsed_seconds
            }

    # __________________________________________

    def test_hba_adapter_revision(self):
        name = 'test_hba_adapter_revision'
        logger.info("STEP: {} HBA {}: Verifying HBA adapter revision".format(
            self.node['name'], self.adapter['sn']), extra={'color': 'blue'})
        result = {'name': name}
        supported_revisions = self.params['isp']['supported']['revisions']
        logger.debug("HBA Adapter Supported revisions: {}".format(supported_revisions))

        if self.port['revision'] not in supported_revisions:
            logger.error("{} HBA adapter {}: FC port revision {} is not supported".format(
                self.node['name'], self.adapter['sn'], self.port['revision']), extra={'color': 'red'})
            result.update({'status': False})
            return result

        logger.info("{} HBA {}: HBA adapter revision is supported".format(self.node['name'], self.adapter['sn']))
        result.update({'status': True})
        return result
    # ______________________________________________

    def test_sfp_model(self):
        name = 'test_sfp_model'
        logger.info("STEP: {} HBA {}: Verifying SFP model being supported".format(
            self.node['name'], self.adapter['sn']), extra={'color': 'blue'})
        result = {'name': name}
        supported_sfps = self.params['sfp']['supported']

        mediainfo = self.port['sfp']['mediainfo']
        logger.debug("{} MEDIAINFO: {}".format(self.port['wwpn'], mediainfo))

        if mediainfo['PartNumber'] in supported_sfps.keys():
            status = True
            logger.info("{} HBA {}: {} passed - all SFP models are supported".format(
                self.node['name'], self.adapter['sn'], name), extra={'color': 'green'})
        else:
            logger.error("{} {} {}: SFP part number {} is not in supported list".format(
                self.node['name'],
                self.adapter['sn'],
                self.port['wwpn'],
                mediainfo['PartNumber']),
                extra={'color': 'red'}
            )
            status = False

        result.update({'status': status})
        logger.info("{}: RESULT: {}".format(name, result))
        return result
    # ______________________________________________

    def test_external_loopback(self):
        name = 'external_loopback'
        loopback_type = self.params[name]['type']
        return self.run_loopback_test(name, loopback_type)
    # ______________________________________________

    def test_internal_loopback_bit1(self):
        name = 'internal_loopback_bit1'
        loopback_type = self.params[name]['type']
        return self.run_loopback_test(name, loopback_type)
    # ______________________________________________

    def test_sfp_revision(self):
        """
        """
        step_name = 'test_sfp_revision'
        logger.info("STEP {}: verifying SFP revisions are supported".format(step_name), extra={'color': 'blue'})
        result = {'name': step_name}

        supported_revisions = self.params['sfp']['supported'][self.port['sfp']['mediainfo']['PartNumber']]
        logger.debug("FC Adapater Supported revisions: {}".format(supported_revisions))
        logger.debug("Supported revisions: {}".format(supported_revisions))

        if self.port['sfp']['mediainfo']['Revision'] in supported_revisions:
            logger.info("{} HBA {}: {} passed".format(
                self.node['name'], self.adapter['sn'], step_name), extra={'color': 'green'})
            status = True
        else:
            logger.error("{} {} {}: SFP revision {} is not supported".format(
                self.node['name'], self.adapter['sn'],
                self.port['wwpn'], self.port['gbic']['PartNumber']), extra={'color': 'red'})
            status = False

        result.update({'status': status})
        return result
    # ______________________________________________

    def test_sfp_diagnostics(self):
        """FC port SFP diagnostics.

        """
        step_name = 'test_sfp_diagnostics'
        result = {'name': step_name}
        node_hostname = self.node['name']
        adapter_name = '%s-%s' % (self.adapter['model'], self.adapter['sn'])

        logger.info("STEP: {}: Running transceiver tests on HBA adapter {}".format(
            node_hostname, adapter_name), extra={'color': 'blue'})

        diag = self.port['sfp']['diagnostics']

        logger.debug("{} {}: diagnostics data: {}".format(node_hostname, adapter_name, pprint.pformat(diag)))

        for param in diag.keys():
            if diag[param]['Status'] == 'Normal':
                logger.info("{} {}: {} passed".format(node_hostname, adapter_name, step_name), extra={'color': 'green'})
                status = True
            else:
                status = False
                logger.error("{} {}: {} failed".format(
                    node_hostname, adapter_name, step_name), extra={'color': 'red'})

        result.update({'status': status})
        return result
    # ______________________________________________

    def validate_loopback_diagnostics(self, output):
        """
        Example for XML output:

        <?xml version="1.0" encoding="ISO-8859-1"?>
            <QLogic>
                <AppName>QLogic FCAPI</AppName>
                <AppVersion>v1.7.3 Build 68</AppVersion>
                <HBA>
                    <HBA Port="2" WWNN="20-00-00-24-FF-82-C2-06" WWPN="21-00-00-24-FF-82-C2-06" />
                    <Loop ID="00-00-EF" CRCError="0" DisparityError="0" FrameLengthError="0" Result="Success"/>
                </HBA>
                <Status> 0 </Status>
                <Reboot> 0 </Reboot>
            </QLogic>
        """

        import xml.etree.ElementTree as et
        root = et.fromstring(output)
        p = './HBA/Loop'
        diag = root.find(p)

        if diag.attrib['Result'].lower() == 'success':
            return True
        else:
            return False
# =====================================
