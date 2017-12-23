import time
from lib.decorators import task
from srv.lib.basetask import Basetask
# =============================


class Test_system_drives(Basetask):

    @task
    def run(self):
        while True:
            time.sleep(1)
    # _________________________________________________

    def get_result(self):
        return {'result': None}

# ================================================
