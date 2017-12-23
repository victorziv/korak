import time
from lib.decorators import task
from srv.lib.basetask import Basetask
# =====================================


class Platform_install(Basetask):

    @task
    def __call__(self):
        self.logger.info("PLATFORM INSTALLATION")
        while True:
            time.sleep(1)
    # _________________________________________________

    def get_result(self):
        self.logger.info("PLATFORM INSTALLATION RESULT")
        return {'result': None}
