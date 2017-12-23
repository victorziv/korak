import time
from srv.lib.registry import testcase
from config import logger
# _______________________________


@testcase()
def qlogic_fcloopback():
    """
    :Attributes:
    author: tmcmillan
    owner: tmcmillan'
    created:2017-05-08
    """

    logger.info('running qlogic_fcloopback()')
    time.sleep(10)
    logger.info("==> qlogic_fcloopback finishes")
    return True


@testcase(active=True)
def qlogic_connected_to_switch():
    """Checks QLogic FC ports connected to Bazinga switch.

    :Attributes:
        author: bobo
        category: hba_adapter
        owner: zaphod
        created: 2017-04-03
    """

    # Attributes
    author='mzuchmer' # noqa
    owner='juliette' # noqa
    created='2017-05-06' # noqa
    # /Attributes

    logger.info('''Some of qLogic ports are connected to FC switch.''')
    time.sleep(25)
    logger.info("==> qlogic_connected_to_switch finishes")
    return True
