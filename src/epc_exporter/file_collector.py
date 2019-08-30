"""
File collector collects the EPC cli outputs and exports them to
a pom file as configured
"""

import os
import signal
import sys
import time

from prometheus_client import REGISTRY, write_to_textfile

from collector import register_collectors
from device import RemoteDevice, TestDevice


class GracefulKiller:
    """GracefulKiller watches for SIGINT and SIGTERM events and set a flag"""

    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        """sets the state to indicate that application should exit now"""
        print('Received signal event, %s %s', signum, frame)
        self.kill_now = True


if __name__ == "__main__":
    # Running in text collector mode
    TEMPLATES_PATH = sys.argv[1]
    OUTPUT_PATH = sys.argv[2]

    KILLER = GracefulKiller()

    TEST_DATA_PATH = os.environ.get('FILE_DEVICE')
    if TEST_DATA_PATH is not None:
        DEVICE = TestDevice(TEST_DATA_PATH)
    else:
        DEVICE = RemoteDevice(
            os.environ['DEVICE_HOSTNAME'], os.environ["DEVICE_USERNAME"],
            os.environ["DEVICE_PASSWORD"], os.environ["TEST_PASSWORD"])

    COLLECTION_FREQ = os.environ.get('FREQ')
    if COLLECTION_FREQ is not None:
        COLLECTION_FREQ = int(COLLECTION_FREQ)
    else:
        COLLECTION_FREQ = 60

    register_collectors(TEMPLATES_PATH, DEVICE)

    while not KILLER.kill_now:
        DEVICE.start_session()
        write_to_textfile(OUTPUT_PATH, REGISTRY)
        DEVICE.stop_session()

        for x in range(int(COLLECTION_FREQ / 5)):
            if not KILLER.kill_now:
                time.sleep(5)
