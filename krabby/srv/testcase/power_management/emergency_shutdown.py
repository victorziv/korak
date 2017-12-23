import time
from srv.lib.registry import testcase
from config import logger
# _____________________________________


@testcase()
def emergency_shutdown():
    logger.info('+++++++++++++ Testing emergency shutdown')
    time.sleep(10)
    logger.info("=====> Emergency_shutdown finishing")
# _____________________________________
