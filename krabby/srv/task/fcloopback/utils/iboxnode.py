import os
import time
import datetime
from infinilab_api import Infinilab
from config import tasklogger as logger
from srv.lib.oshelper import (
    scp_file_with_pswd,
    get_idrac_password,
    run_remote_command_with_pswd,
    run_command_in_shell
)
infinilab = Infinilab()
# ________________________________________


def check_smart_tools_installed(node_hostname):
    tool = 'smartmontools'
    cmd = 'rpm -q %s' % tool
    output = run_remote_command_with_pswd(node_hostname, cmd)

    logger.debug("Remote CMD output: {}".format(output))

    if 'is not installed' in output:
        logger.error("{} is not installed on node {}".format(tool, node_hostname))
        return False
    else:
        logger.info("{} is installed on node {}".format(tool, node_hostname))
        return True
# ________________________________________


def check_qconverge_console_cli_installed(node_hostname, params):
    tool = 'QConvergeConsoleCLI'
    tool_installed = 'rpm -qa | grep -i %s' % tool
    check_output = run_remote_command_with_pswd(node_hostname, tool_installed)

    logger.debug("Check tool installed output: {}".format(check_output))

    if not check_output:
        logger.info("{} is not installed on node {}. Trying to install".format(tool, node_hostname))
        install_output = _install_qconverge_console_cli(node_hostname, params)
        logger.info("Install RPM output: {}".format(install_output))

    check_output = run_remote_command_with_pswd(node_hostname, tool_installed)
    if not check_output:
        logger.error("Failed to find {} on node {} - aborting".format(tool, node_hostname))
        return False

    logger.info("Tool {} found installed on on node {}".format(tool, node_hostname))
    return True
# ________________________________________


def check_sg3_utils_installed(node_hostname):
    tool = 'sg3_utils'
    cmd = 'rpm -q %s' % tool
    output = run_remote_command_with_pswd(node_hostname, cmd)

    logger.debug("Remote CMD output: {}".format(output))

    if 'is not installed' in output:
        logger.error("{} is not installed on node {}".format(tool, node_hostname))
        return False
    else:
        logger.info("{} is installed on node {}".format(tool, node_hostname))
        return True
# ________________________________________


def check_qlogic_driver_is_loaded(node_hostname):
    """
    Checks that the stock kernel driver for QLogic HBAs (qla2xxx) is loaded.
    Other drivers are not supported.
    """
    driver = 'qla2xxx'
    cmd = 'modprobe -l %s' % driver
    output = run_remote_command_with_pswd(node_hostname, cmd)

    logger.debug("QLogic driver loaded CMD output: {}".format(output))

    if driver in output:
        logger.info("Driver {} is loaded on node {}".format(driver, node_hostname))
        return True
    else:
        logger.error("Driver {} is not loaded on node {}".format(driver, node_hostname))
        return False
# ________________________________________


def get_server_type(node):
    cmd = 'lspci | grep -i MegaRAID'
    output = run_remote_command_with_pswd(node['name'], cmd)
    if '3108' in output:
        return 'R730'
    else:
        return 'R720'
# ___________________________________


def _install_qconverge_console_cli(node_hostname, params):
    tool = params['tools']['qlogic_converge_console_cli']
    logger.info("Installing {} on node {}".format(tool, node_hostname))
    srcrpm = os.path.join(params['tools_path'], tool)
    dstrpm = "/tmp/%s" % tool

    # First copy the RPM onto the node
    scp_file_with_pswd(node_hostname, srcrpm, dstrpm)

    # Install the RPM package
    install_cmd = 'rpm -U %s' % dstrpm
    output = run_remote_command_with_pswd(node_hostname, install_cmd)
    return output
# ________________________________________


def _node_is_pingable(node_name):

    cmd = "ping -c 1 -W 1 {} > /dev/null 2>&1"

    ret = os.system(cmd.format(node_name))
    if ret == 0:
        result = True
        logger.info("Ping node  {} is OK".format(node_name))
    else:
        result = False
        logger.info("Node {} does not answer to ping".format(node_name))

    return result
# ______________________________________


def node_is_in_dr_state(node_hostname, params):
    """Check an Infinibox node is in D&R state

    Args:
       node_hostname(str): Infinibox Node DNS name.

    Returns:
        bool:
            - True if the node was found rebooted into D&R state
            - False otherwise
    """
    cmd = 'hostname'
    output = run_remote_command_with_pswd(node_hostname, cmd)
    if output.strip() in params['dr_hostnames']:
        logger.info("Node {} is in D&R state".format(node_hostname))
        return True
    else:
        logger.info("Node {} is not in D&R state".format(node_hostname))
        return False
# ____________________________________


def _node_power_cycle_via_idrac(node_hostname):
    logger.info("Power cycling node {}".format(node_hostname))
    idrac_hostname = 'm-%s' % node_hostname
    idrac_password = get_idrac_password()
    cmd = '/usr/bin/ipmitool'
    cmdargs = ['-I lanplus', '-U root', '-P %s' % idrac_password, '-H %s' % idrac_hostname, 'power', 'cycle']
    logger.info("RUN COMMAND IN SHELL: %s %s", cmd, ' '.join(cmdargs))
    output = run_command_in_shell(cmd, cmdargs)
    logger.info("Cmd OUTPUT: {}".format(output))
# ______________________________________


def _set_boot_device(node_hostname, device):
    logger.info("{} Set boot device to {}".format(node_hostname, device))
    idrac_password = get_idrac_password()
    idrac_hostname = 'm-%s' % node_hostname
    cmd = '/usr/bin/ipmitool'
    cmdargs = [
        '-I lanplus',
        '-U root',
        '-P %s' % idrac_password,
        '-H %s' % idrac_hostname,
        'chassis', 'bootdev', device
    ]
    logger.info("RUN COMMAND IN SHELL: %s %s", cmd, ' '.join(cmdargs))
    output = run_command_in_shell(cmd, cmdargs)
    logger.info("Cmd OUTPUT: {}".format(output))
# ____________________________________


def _node_power_cycle(node_hostname):
    logger.info("{}: Power cycling".format(node_hostname))
    idrac_password = get_idrac_password()
    idrac_hostname = 'm-%s' % node_hostname
    cmd = '/usr/bin/ipmitool'
    cmdargs = [
        '-I lanplus',
        '-U root',
        '-P %s' % idrac_password,
        '-H %s' % idrac_hostname,
        'power', 'cycle'
    ]
    logger.info("RUN COMMAND IN SHELL: %s %s", cmd, ' '.join(cmdargs))
    output = run_command_in_shell(cmd, cmdargs)
    logger.info("Cmd OUTPUT: {}".format(output))
# ______________________________________


def put_node_into_dr_state(node_hostname, params):
    """Puts the system nodes into D&R state.

    Args:
        ibox(object): Infinibox system object
    """

    _set_boot_device(node_hostname, 'pxe')
    _node_power_cycle(node_hostname)
    _wait_for_node_go_down(node_hostname)
    timeout = params['timeout_node_state']
    return _wait_for_node_startup(node_hostname, timeout)
# ______________________________________


def put_node_into_ibox_state(node_hostname, params):
    """Brings the node back from D&R state.

    Args:
        node(object): Infinibox node object
    """

    logger.info("{}: Put into IBOX state".format(node_hostname))
    _set_boot_device(node_hostname, 'disk')
    _node_power_cycle(node_hostname)
    _wait_for_node_go_down(node_hostname)
    timeout = params['timeout_node_state']
    return _wait_for_node_startup(node_hostname, timeout)
# ______________________________________


def validate_sw_installed(node, params):
    results = []
    results.append(check_smart_tools_installed(node['name']))
    results.append(check_sg3_utils_installed(node['name']))
    results.append(check_qlogic_driver_is_loaded(node['name']))
    results.append(check_qconverge_console_cli_installed(node_hostname=node['name'], params=params))
    return all(results)
# ______________________________________


def _wait_for_node_go_down(node_hostname, sleep_for=5, timeout=60):

    start = datetime.datetime.now()
    logger.info("Waiting for Node {} to go down".format(node_hostname))
    logger.info("Wait started: {}".format(start))
    logger.info("Timeout is set to {} sec.".format(timeout))

    while True:
        if not _node_is_pingable(node_hostname):
            logger.info("Node {} is inaccessible".format(node_hostname))
            return True

        finish = datetime.datetime.now()
        elapced_time = (finish - start).seconds
        if elapced_time >= timeout:
            msg = "TIMEOUT {} sec. waiting for Node {} to be go down".format(timeout, node_hostname)
            logger.error(msg)
            assert False, "Node {} failed to be powered OFF"

        logger.info("Node {} is still accessible - sleeping for {} sec.".format(node_hostname, sleep_for))
        time.sleep(sleep_for)
# ______________________________________


def _wait_for_node_startup(node_hostname, timeout, sleep_for=30):
    start = datetime.datetime.utcnow()
    logger.info("Waiting for Node {} to start up".format(node_hostname))
    logger.info("Wait started: {}".format(start))
    logger.info("Timeout is set to {} sec.".format(timeout))

    while True:
        if _node_is_pingable(node_hostname):
            logger.info("Node {} is accessible".format(node_hostname))
            return True

        finish = datetime.datetime.utcnow()
        elapced_time = (finish - start).seconds
        if elapced_time >= timeout:
            msg = "TIMEOUT {} sec. waiting for Node {} to be accessible".format(timeout, node_hostname)
            logger.error(msg)
            assert False, msg

        logger.info("Node {} is not accessible yet - sleeping for {} sec.".format(node_hostname, sleep_for))
        time.sleep(sleep_for)
# ______________________________________
