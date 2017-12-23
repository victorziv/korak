import os
import json
import time
import queue
from config import tasklogger as logger
# =====================================


class Sink:
    def __init__(self, params):
        self.params = params
    # ________________________________

    def __call__(self, queue_done):
        self.queue_done = queue_done
        results = []
        try:
            while True:
                time.sleep(1)
                try:
                    result = queue_done.get_nowait()
                    if type(result).__name__ == 'str' and result.upper() == 'QUIT':
                        logger.debug("Sink: Got QUIT, as quitting")
                        break

                    if result is None:
                        continue

                    logger.info("Sink: Result ( Node {}, adapter {}, port {} ) arrived: {}".format(
                        result['node'], result['adapter'], result['port'], result))
                    results.append(result)

                except queue.Empty:
                    continue

            self.save_result(results)

        except Exception as e:
            logger.exception("!SINK Exception")
            raise

    # __________________________________

    def save_result(self, results):
        logger.debug("Saving results: {}".format(results))
        result_file = os.path.join(os.path.dirname(logger.pathinfo), '%s.json' % self.params['taskname'])

        with open(result_file, 'w') as fh:
            json.dump(results, fh)

# =====================================
