import time
from lib.decorators import task
from srv.lib.basetask import Basetask
# =============================


class Mfg_test_suite(Basetask):

    @task
    def __call__(self):
        while True:
            time.sleep(1)
    # _________________________________________________

    def get_result(self):
        return {'result': None}

# ================================================
