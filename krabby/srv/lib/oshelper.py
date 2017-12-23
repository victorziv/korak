import os
import signal
import time
import subprocess
import paramiko
import datetime
from config import conf
# ____________________________


def _create_paramiko_ssh_client(dstserver, username, password, port=22):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(dstserver, port, username, password)
    return ssh
# ____________________________


def create_ssh_directory(node_hostname):
    """
    Not in use currently.
    """
    pxe_passwd = get_pxe_password()
    cmd = 'mkdir ~/.ssh'
    runssh_pswd_auth(
        dsthost=node_hostname,
        user=conf['NODE_USER'],
        pswd=pxe_passwd,
        cmd=cmd
    )
# ________________________________________


# datetime.datetime.now().strftime('%Y%m%d%H%M%S-%f')
# ________________________________________


def get_idrac_password():
    pfile = os.path.expanduser('~/.infinidat/.ivtidrac')
    with open(pfile) as pf:
        pswd = pf.read().strip()

    return pswd
# ____________________________


def get_pxe_password():
    pfile = os.path.expanduser('~/.infinidat/.ivtpxe')
    with open(pfile) as pf:
        pswd = pf.read().strip()

    return pswd
# ____________________________


def copy_file_with_pswd(dsthost, user, pswd, srcpath, dstpath=None, port=22, override=False):
    """
    Copies a file to the dstserver.
    First checks if not already exists.
    Skips copying if it does.
    Overrides if *override* parameter is set to True. Default: False
    """

    if dstpath is None:
        dstpath = srcpath

    try:
        client = _create_paramiko_ssh_client(dsthost, user, pswd)
        sftp = client.open_sftp()
        if override:
            sftp.put(srcpath, dstpath)
        else:
            try:
                sftp.stat(dstpath)
            except IOError:
                sftp.put(srcpath, dstpath)
    finally:
        client.close()

# ____________________________


def put_public_ssh_key_to_node_in_dr(node_hostname):
    """
    DEPRECATED: Not in use currently.
    """
    create_ssh_directory(node_hostname)

    pxe_passwd = get_pxe_password()
    public_key_file = os.path.expanduser("~/.ssh/id_rsa.pub")
    public_key_string = open(public_key_file).read().strip()
    cmd = 'echo %s >> ~/.ssh/authorized_keys' % public_key_string
    runssh_pswd_auth(
        dsthost=node_hostname,
        user=conf['NODE_USER'],
        pswd=pxe_passwd,
        cmd=cmd
    )

# ________________________________________


def run_command_in_shell(cmd, cmdargs=None, timeout=None, logger=None):

    if cmdargs is None:
        args = []
    else:
        args = list(cmdargs)

    exception = ''
    err = ''
    out = ''
    args.insert(0, cmd)
    execline = ' '.join(args)

    p = subprocess.Popen(
        execline,
        env=os.environ,
        shell=True,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    if timeout:
        start = datetime.datetime.now()
        while p.poll() is None:
            time.sleep(0.5)
            now = datetime.datetime.now()
            if (now - start).seconds > timeout:
                os.kill(p.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
                p.returncode = 1
                err = "command %s failed on timeout of %s sec" % (execline, timeout)
                return (p.pid, p.returncode, exception, out, err)

    out, err = p.communicate()
    return (p.pid, p.returncode, '', out, err)
# __________________________________________


def runssh(dst, cmd):
    with subprocess.Popen(
        ['ssh', '-o UserKnownHostsFile=/dev/null', '-o StrictHostKeyChecking=no', dst, cmd],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ) as ssh:

        output = ssh.stdout.readlines()

        if not output:
            output = []

    return output
# ___________________________________


def runssh_pswd_auth(dsthost, user, pswd, cmd, port=22):
    try:
        client = None
        client = _create_paramiko_ssh_client(dsthost, user, pswd)
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read()
        return out

    except paramiko.ssh_exception.BadAuthenticationType:
        return b''

    finally:
        if client:
            client.close()
# ________________________________________


def run_remote_command_with_pswd(node_hostname, cmd):

    pxe_passwd = get_pxe_password()
    output = runssh_pswd_auth(
        dsthost=node_hostname,
        user=conf['NODE_USER'],
        pswd=pxe_passwd,
        cmd=cmd
    )

    return output.decode('utf-8').strip()

# ________________________________________


# def run_remote_command_on_idrac(node_hostname, cmd):

#     idrac_passwd = get_idrac_password()
#     output = runssh_pswd_auth(
#         dsthost=node_hostname,
#         user=conf['NODE_USER'],
#         pswd=pxe_passwd,
#         cmd=cmd
#     )

#     return output.decode('utf-8').strip()

# ________________________________________


def run_qaucli_command(node_hostname, param_string):
    cmd = '/usr/local/bin/qaucli %s' % param_string
    output = run_remote_command_with_pswd(node_hostname, cmd)
    return output
# __________________________________________


def scp_file_with_pswd(node_hostname, srcfile, dstfile):

    pxe_passwd = get_pxe_password()
    copy_file_with_pswd(
        dsthost=node_hostname,
        user=conf['NODE_USER'],
        pswd=pxe_passwd,
        srcpath=srcfile,
        dstpath=dstfile
    )
# ________________________________________
