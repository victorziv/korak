import re
import pprint
import xml.etree.ElementTree as ET

from srv.lib.oshelper import (
    runssh,
    run_remote_command_with_pswd,
    run_qaucli_command
)

from config import tasklogger as logger

PORT_QUERY_CMD = "infinishell -u infinidat -p 123456 localhost -c config.fc.port.query"
PORT_MNG_CMD = 'infinishell localhost -u infinidat -p 123456 -c "config.fc.port.{} port={}"'
# ___________________________________


def _find_card_addresses(node, adapters, params):

    pci_slots = _find_pci_slots(node, params)
    cmd_tmpl = 'lspci -vv -s {}'
    pattern = re.compile(r'\s*\[SN\]\s+Serial\s+number:\s*(\S+)$', flags=re.IGNORECASE)

    slots = {}
    for pci_slot in pci_slots:
        cmd = cmd_tmpl.format(pci_slot)
        output = run_remote_command_with_pswd(node['name'], cmd)

        for line in output.splitlines():
            line = line.strip()
            m = pattern.match(line)
            if m:
                sn = m.group(1)
                slots.setdefault(sn, []).append(pci_slot)
                break

    logger.debug("SLOTS: {}".format(slots))

    return slots
# ___________________________________


def _find_pci_slots(node, params):
    pci_addresses = []
    supported_pci_key = params['isp']['supported']['pci_key']
    pattern = re.compile(
        r'^([0-9a-fA-F]{1,4}:[0-9a-fA-F]{1,4}\.[0-9a-fA-F]{1})\s+\S+:\s+%s\s+\(rev\s+\d+\)$' % supported_pci_key
    )

    cmd = '/sbin/lspci -n | grep %s 2>&1' % supported_pci_key
    output = run_remote_command_with_pswd(node['name'], cmd)

    for line in output.splitlines():
        pci_addresses.append(pattern.match(line.strip()).group(1))

    return pci_addresses
# ___________________________________


def assign_card_locations(node, adapters, params):
    slots = _find_card_addresses(node, adapters, params)
    node_conf = params['isp']['pci_locations'][node['server_type']]
    for sn in slots.keys():
        for adapter in adapters:
            if adapter['sn'] == sn:
                adapter['location'] = node_conf[frozenset(slots[sn])]
                break

    return adapters
# ___________________________________


def detect_hba_adapters(node_hostname):
    """Detects QLogic HBA adapters by running quacli command on the node

    Args:
       node_hostname(str): a node hostname

    Returns:
        list: a list of dictionaries with a dictionary per detected adapter
              or empty list if no adapters were detected.
    """
    cmd_params = '-pr fc -g'
    output = run_qaucli_command(node_hostname, cmd_params)
    adapters = _parse_hba_adapters_output(output.strip())
    return adapters
# ________________________________________


def disable_fcports(ibox, fcports=None):

    """ Disables those FC ports that are in *enabled* state and have a loopback installed.

    While running an IVT automatic test session the function is triggered before any test case starts
    in order to provide the working setup for IO traffic.

    Args:
        ibox(object): Infinibox SDK object
        fcports(list): Optional. A list of FC ports to disable. Default is None.
                       If *fcports* list is provided every included port must to be in enabled state
                       and have a loopback installed
    """

    enabled_ports_with_loopbacks = get_enabled_ports_with_loopback(ibox)

    if fcports is None:
        fcports = enabled_ports_with_loopbacks

    elif set(fcports) & set(enabled_ports_with_loopbacks) != set(fcports):
        assert False, "Not all provided fcports {} can be disabled".format(fcports)

    logger.info("Disabling FC ports with loopback on ibox {}: {}".format(ibox, fcports))
    for port in fcports:
        _disable_fc_port_via_infinishell(ibox, port)
# ___________________________________


def _disable_fc_port_via_infinishell(ibox, port):
    cmd = PORT_MNG_CMD.format('disable', port)
    output = runssh(ibox, cmd)
    logger.info("Disable FC port {} output: {}".format(port, output))

# ___________________________________


def enable_fcports(ibox, fcports=None):

    """Enables those FC ports that are in *disabled* state.

    While running an IVT automatic test session the function is triggered after all test cases finish
    in order to restore the factory default Infinibox machines in IVT

    Args:
        ibox(object): Infinibox SDK object
        fcports(list): Optional. A list of FC ports to disable. Default is None.
                       If *fcports* list is provided every included port must to be in disables state
    """

    disabled_ports = _get_disabled_ports(ibox)
    if fcports is None:
        fcports = disabled_ports

    elif set(fcports) & set(disabled_ports) != set(fcports):
        assert False, "Not all provided fcports {} can be enabled".format(fcports)

    logger.info("Enabling FC ports on ibox {}: {}".format(ibox, fcports))
    for port in fcports:
        _enable_fc_port_via_infinishell(ibox, port)
# ___________________________________


def _enable_fc_port_via_infinishell(ibox, port):
    cmd = PORT_MNG_CMD.format('enable', port)
    output = runssh(ibox, cmd)
    logger.info("Enable FC port {} output: {}".format(port, output))
# ___________________________________


# def fetch_fc_port_state_by_node(node):
#     """Fetches QLogic ports state from an Infinibox node.

#     Connects to the node via SSH and uses QLogic qladm command
#     to figure out FC ports state.

#     Args:
#         ibox(object): Infinibox system object

#     Returns:
#         dict: A dictionary where a key is the node objects and the value is a list containing FC ports states.

#     """

#     cmd_template = "qladm --id {} -n state"
#     fc_ports = node['fc_ports']
#     logger.debug("{}: FC ports found: {}".format(node['name'], [fc['port_num'] for fc in fc_ports]))
#     states = []
#     for fc_port in fc_ports:
#         logger.debug("FC port: {}".format(fc_port))
#         output = run_remote_command_with_pswd(node['name'], cmd_template.format(int(fc_port['port_num']) - 1))
#         logger.info("node {}, port {}, output: {}".format(node['name'], fc_port['port_num'], output))

#         if not output:
#             continue

#         state = output[0].decode('utf-8').split('-', 2)[1].strip()
#         states.append((fc_port['port_num'], state))

#     logger.info("Node {} FC ports state: {}".format(node['name'], states))
#     return states
# ___________________________________

def _parse_fc_port_general_info(output):
    root = ET.fromstring(output)
    genpath = './HBA/GeneralInfo'
    gen = root.find(genpath)
    connection_mode = gen.attrib['ActualConnectionMode'].strip().lower()
    return {'connection_mode': connection_mode}
# ___________________________________


def _parse_fcport_revision(output):

    root = ET.fromstring(output)
    vpdpath = './HBA/VPD/VPD'
    vpd = root.find(vpdpath)
    revision = vpd.attrib['ManufacturingId'].split()[1].strip()
    return revision
# ___________________________________


def collect_general_info(node, adapters):
    node_hostname = node['name']
    cmd_params_tmpl = '-pr fc -i {} -x'
    for adapter in adapters:
        for port in adapter['ports']:
            cmd_params = cmd_params_tmpl.format(port['wwpn'])
            output = run_qaucli_command(node_hostname, cmd_params)
            port.update(_parse_fc_port_general_info(output))
            logger.debug("%s %s %s: Connection mode: %s",
                node['name'], adapter['sn'], port['wwpn'], port['connection_mode'])  # noqa
    return adapters
# ___________________________________


def collect_vpd_info(node, adapters):
    node_hostname = node['name']
    cmd_params_tmpl = '-pr fc -i {} vpd -x'
    for adapter in adapters:
        for port in adapter['ports']:
            cmd_params = cmd_params_tmpl.format(port['wwpn'])
            output = run_qaucli_command(node_hostname, cmd_params)
            port['revision'] = _parse_fcport_revision(output)
    return adapters
# ___________________________________


def fetch_transceiver_data(node_hostname, wwpn):
    """Runs diagnostics and fetches the relevant info on FC port transceiver

    Args:
       node_hostname(str): a node hostname
       adapter(dict): HBA adapter parameters dictionary

    Returns:
        list: a list of dictionaries with a dictionary per detected adapter
              or empty list if no adapters were detected.
    """
    cmd_params = '-pr fc -dm %s gen -x' % wwpn
    output = run_qaucli_command(node_hostname, cmd_params)
    data = _parse_fcport_transceiver_output(output.strip())
    return data
# ________________________________________


def _get_disabled_ports(ibox):
    ports = []

    lines = _query_fc_ports(ibox)
    for line in lines:
        port, state = tuple(line.split()[0:2])
        if state == 'no':
            ports.append(port)

    return ports
# __________________________________________


def get_enabled_ports_with_loopback(ibox):
    lines = _query_fc_ports(ibox)

    ports = []
    for line in lines:
        entries = line.split()
        port = entries[0]
        enabled = entries[1]
        link = entries[4]
        switch = entries[5]

        if enabled.lower() == 'yes' and link.lower() == 'up' and switch == '-':
            ports.append(port)

    return ports
# __________________________________________


def _get_enabled_ports_with_loopback_via_monitorsh(ibox):
    """
    DEPRECATED and not used currently as less reliable.
    If a port is disabled - connection is rejected.
    """
    ports = []
    node_pat = re.compile(r'\[\s*node\s+(\d{1})\s*\]')
    loop_port_pat = re.compile(r'Port\s+(\d{1}):\s*Link\s*Up\s*-\s*Loop', re.IGNORECASE)

    sa = 'm-{}'.format(ibox)
    cmd = '/opt/infinidat/sa-utils/monitor.sh --fc-links'
    output = runssh(sa, cmd)[3:]

    for l in output:
        line = l.strip().decode('utf-8')
        node_match = node_pat.search(line)
        if node_match:
            node = 'N{}'.format(node_match.group(1))
        else:
            loop_port = loop_port_pat.search(line)
            if loop_port:
                ports.append('{}FC{}'.format(node, loop_port.group(1)))

    return ports
# __________________________________________


def _parse_fcport_transceiver_output(output):

    logger.debug("Output to parse: {}".format(output))

    data = {
        'diagnostics': {},
        'mediainfo': {}
    }

    diagnostic_path = './HBA/Diagnostics'
    media_info_path = './HBA/MediaInformation'

    root = ET.fromstring(output)

    # Parse diagnostics
    diag_els = []
    for ch in root.find(diagnostic_path):
        diag_els.append(ch)
        data['diagnostics'][ch.tag] = {}

    for el in diag_els:
        tag_name = el.tag.strip()
        for ch in root.find('%s/%s' % (diagnostic_path, tag_name)):
            data['diagnostics'][tag_name][ch.tag] = ch.text.strip()

    # Parse MediaInformation
    for ch in root.find(media_info_path):
        data['mediainfo'][ch.tag] = ch.text.strip()

    logger.debug("Transceiver data: {}".format(pprint.pformat(data)))
    return data
# __________________________________________


def _parse_hba_adapters_output(output):
    """
    cmd: qaucli -pr fc -g
    output example:

    --------------------------------------------------------------------------------
    Host Name                      : infiniconf
    OS Type                        : Linux - CentOS release 6.6  x86_64
    OS Version                     : 2.6.32-504.3.3.el6.x86_64
    FO API Version                 : 3.0.1 build7
    SDM API Version                : v6.03 build9
    --------------------------------------------------------------------------------
    HBA Model QLE2564 (SN RFD1651N76456):
      Port   1 WWPN 21-00-00-24-FF-82-C2-00 (HBA instance  4) Online
      Port   2 WWPN 21-00-00-24-FF-82-C2-01 (HBA instance  5) Online
      Port   3 WWPN 21-00-00-24-FF-82-C2-02 (HBA instance  6) Online
      Port   4 WWPN 21-00-00-24-FF-82-C2-03 (HBA instance  7) Online
    HBA Model QLE2564 (SN RFD1651N76677):
      Port   1 WWPN 21-00-00-24-FF-82-C3-E8 (HBA instance  0) Online
      Port   2 WWPN 21-00-00-24-FF-82-C3-E9 (HBA instance  1) Online
      Port   3 WWPN 21-00-00-24-FF-82-C3-EA (HBA instance  2) Online
      Port   4 WWPN 21-00-00-24-FF-82-C3-EB (HBA instance  3) Online
    --------------------------------------------------------------------------------
    Total QLogic HBA(s) : 2

    """
    hba_pat = re.compile(r'\s*HBA\s+Model\s+(\S+)\s+\(SN\s+(\S+)\)', flags=re.IGNORECASE)
    port_pat = re.compile(r'\s*Port\s+(\d+)\s+WWPN\s+(\S+)\s+\(HBA\s+instance\s+(\d+)\)\s+(\S+)$', flags=re.IGNORECASE)

    adapters = []
    for line in [l.strip() for l in output.splitlines()]:

        if not line:
            continue

        hba_match = hba_pat.match(line)
        if hba_match:
            ad = {
                'model': hba_match.group(1),
                'sn': hba_match.group(2),
                'ports': []
            }

            adapters.append(ad)
        elif port_pat.match(line):
            port_match = port_pat.match(line)
            ad['ports'].append({
                'port_number': port_match.group(1),
                'wwpn': port_match.group(2),
                'hba_instance': port_match.group(3),
                'status': port_match.group(4).lower()
            })

    logger.debug("--- HBA Adapters found ----")
    logger.debug(pprint.pformat(adapters))

    return adapters
# __________________________________________


def _query_fc_ports(ibox):
    output = runssh(ibox, PORT_QUERY_CMD)[1:]
    lines = [o.strip().decode('utf-8') for o in output]
    return lines
# __________________________________________
