import time
from lib.decorators import task
from srv.lib.basetask import Basetask
# =============================


class Hw_wizard(Basetask):

    @task
    def __call__(self):
        while True:
            time.sleep(1)
    # _________________________________________________

    def get_result(self):
        return {'result': None}

# ================================================
