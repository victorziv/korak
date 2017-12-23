import time
from lib.decorators import task
from srv.lib.basetask import Basetask
# ====================================


class Checkall(Basetask):

    @task
    def __call__(self):
        self.logger.info("Starting task %s", self.params['taskname'])
        while True:
            time.sleep(1)
    # _________________________________________________

    def get_result(self):
        self.logger.info("Getting task %s result", self.params['taskname'])
        return {'result': None}

# ================================================
