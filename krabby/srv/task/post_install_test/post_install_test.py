import time
from lib.decorators import task
from srv.lib.basetask import Basetask
# =============================


class Post_install_test(Basetask):

    @task
    def __call__(self):
        while True:
            time.sleep(1)
    # _________________________________________________

    def get_result(self):
        return {'result': None}

# ================================================
