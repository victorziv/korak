import time
import datetime
import pprint
from infinilab_api import Infinilab
from config import tasklogger as logger

from srv.lib.oshelper import runssh
infinilab = Infinilab()
# ________________________________________


def activate_system(ibox, timeout):

    logger.info("Activating {0}".format(ibox))
    sa = 'm-%s' % ibox
    cmd = "infinishell %s -u infinidat -p 123456 -c system.activate" % ibox
    output = runssh(sa, cmd)
    logger.info("Activate system output: {}".format(output))
#     timeout = params['timeout_services_start']
    return _wait_for_system_to_become_active(ibox, timeout)
# ________________________________________


def check_hwstatus(ibox_name):
    """ Runs hwstatus.sh utility script on the Infinibox Support Appliance (SA).

    HWStatus output is parsed and the *System status* entry is looked up.

    .. code-block:: bash

        $ ssh m-ibox1692
        # /opt/infinidat/sa-utils/hwstatus.sh

    Args:
        ibox(obj): Infinibox system object

    Returns:
        bool:
            - True if *System status: OK* was found in the output,
            - False if *System status: Not OK* was found.
    """

    logger.info("Running HWStatus on Ibox {}".format(ibox_name))
    cmd = '/bin/bash /opt/infinidat/sa-utils/hwstatus.sh'
    output = runssh('m-%s' % ibox_name, cmd)
    logger.info("HWStatus Output: {}".format(pprint.pformat(output)))
    status = output[-1].decode('utf-8').split(':')[1].strip()
    logger.debug("Status: {}".format(status))

    if status.upper() == 'OK':
        return True
    else:
        return False
# ______________________________________


def get_nodes_from_infinilab(ibox_name, node_filter=None):

    logger.info('Reading node information for {0} from Infinilab'.format(ibox_name))
    iboxtaskcondf = infinilab.resolve_ver(ibox_name)['config']
    for rack in iboxtaskcondf['racks']:
        nodes = [
            _set_node_params(ibox_name, node)
            for node in rack['nodes']
            if (node_filter is None or str(node['location']) in node_filter)
        ]
        logger.info("Nodes filtered: {}".format([n['location'] for n in nodes]))

    return nodes
# ______________________________________


def get_system_state(ibox):

    sa = 'm-%s' % ibox
    cmd = "infinishell %s -u infinidat -p 123456 -c system.info |  grep -i 'operational state'" % ibox
    output = runssh(sa, cmd)
    logger.info("System state OUTPUT: {}".format(output))
    if len(output):
        state = output[0].split()[-1].strip().decode('utf-8')
        logger.info("System {} state: {}".format(ibox, state))
        return state
    else:
        return ''
# ______________________________________

# def _node_power_cycle_dr(node_hostname):
#     logger.info("Power cycling node {}".format(node_hostname))
#     cmd = 'ipmitool power cycle'
#     output = run_remote_command_with_pswd(node_hostname, cmd)
#     logger.info("Cmd OUTPUT: {}".format(output))
# ______________________________________


def _set_node_params(ibox_name, node):
    node['name'] = '{0}-{1}'.format(ibox_name, node['location'])
    return node
# ______________________________________


def restart_ibox_services(ibox, timeout):
    sa = 'm-%s' % ibox
    logger.info("{}: Restarting services".format(sa))
    cmd = "/opt/infinidat/sa-utils/ssh-all.sh xn-depctl --restart"
    runssh(sa, cmd)
    return _wait_for_infinishell_to_start(ibox, timeout)
# ______________________________________


def stop_ibox_services(ibox, services):

    sa = 'm-%s' % ibox
    logger.info("SA found: {}".format(sa))
    for service in services:
        logger.info("Stopping service on nodes: {}".format(service))
        cmd = "/opt/infinidat/sa-utils/ssh-all.sh xn-depctl --stop %s" % service
        runssh(sa, cmd)
# ______________________________________


def system_is_active(ibox):
    if get_system_state(ibox).lower() == 'active':
        return True
    else:
        return False
# ______________________________________


def system_is_standby(ibox):
    if get_system_state(ibox).lower() == 'standby':
        return True
    else:
        return False
# ______________________________________


def system_is_up(ibox):
    if get_system_state(ibox).lower() in ['standby', 'active']:
        return True
    else:
        return False
# ______________________________________


def _wait_for_infinishell_to_start(ibox, timeout, sleep_for=5):
    start = datetime.datetime.now()
    logger.info("Waiting for {} Infinishell to start".format(ibox))
    logger.info("Wait started: {}".format(start))
    logger.info("Timeout is set to {} sec.".format(timeout))

    while True:
        if system_is_up(ibox):
            logger.info("{} Infinishell is UP".format(ibox))
            return True

        finish = datetime.datetime.now()
        elapced_time = (finish - start).seconds
        if elapced_time >= timeout:
            msg = "TIMEOUT {} sec. waiting for {} Infinishell to start".format(timeout, ibox)
            logger.error(msg)
            return False

        logger.info("{} Infinishell is not accessible yet - sleeping for {} sec.".format(ibox, sleep_for))
        time.sleep(sleep_for)
# ______________________________________


def _wait_for_system_to_become_active(ibox, timeout, sleep_for=5):
    start = datetime.datetime.now()
    logger.info("Waiting for Ibox system {} to become active".format(ibox))
    logger.info("Wait started: {}".format(start))
#     if timeout is None:
#         timeout = taskconf['timeout_services_start']
    logger.info("Timeout is set to {} sec.".format(timeout))

    while True:
        if system_is_active(ibox):
            logger.info("System {} is in ACTIVE state".format(ibox))
            return True

        finish = datetime.datetime.now()
        elapced_time = (finish - start).seconds
        if elapced_time >= timeout:
            msg = "TIMEOUT {} sec. waiting for system {} to become active".format(timeout, ibox)
            logger.error(msg, extra={'color': 'red'})
            raise RuntimeError("Timeout on system activation")

        logger.info("System {} is not active yet - sleeping for {} sec.".format(ibox, sleep_for))
        time.sleep(sleep_for)
# ______________________________________
