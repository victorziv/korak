import time
from srv.lib.registry import testcase
from config import logger
# _____________________________________


@testcase()
def qlogic_fcadapter():
    """
    Very basic FC adapter diagnostic. Better than nothing though
    """
    logger.info('+++++++++++++ FC adapter is blowing in the wind')
    time.sleep(3)
    logger.info("=====> FC adapter dropped dead")
# _____________________________________
