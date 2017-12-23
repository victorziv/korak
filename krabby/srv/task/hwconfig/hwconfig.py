import time
from lib.decorators import task
from srv.lib.basetask import Basetask
# =============================


class Hwconfig(Basetask):

    @task
    def __call__(self):
        self.logger.info("Task %s params: %r", self.params['taskname'], self.params)
        self.logger.info("COLOR MESSAGE", extra={"color": "blue"})
        self.logger.info("BOLD COLOR MESSAGE", extra={"color": "green", "strong": True})
        self.logger.info("EMPHASIZED COLOR MESSAGE", extra={"color": "brown", "italic": True})
        self.logger.info("UNDERLINED COLOR MESSAGE", extra={"color": "magenta", "underline": True})
        self.logger.warning("URGENT MESSAGE", extra={"color": "red", "underline": True})
        while True:
            time.sleep(1)
    # _________________________________________________

    def get_result(self):
        self.logger.debug("Getting task %s result", self.params['taskname'])
        return {'result': None}

# ================================================
