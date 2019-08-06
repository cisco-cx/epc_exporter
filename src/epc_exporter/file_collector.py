import signal
import sys
import time

from prometheus_client import REGISTRY, write_to_textfile

from collector import NPUUtilizationCollector, PortUtilizationCollector, PortDataLinkCounterCollector
from device import TestDevice


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


if __name__ == "__main__":
    "Running in text collector mode"
    templates_path = sys.argv[1]
    test_data_path = sys.argv[2]
    output_path = sys.argv[3]

    killer = GracefulKiller()

    device = TestDevice(test_data_path)

    NPUUtilizationCollector(templates_path, device)
    PortUtilizationCollector(templates_path, device)
    PortDataLinkCounterCollector(templates_path, device)

    while not killer.kill_now:
        write_to_textfile(output_path, REGISTRY)
        for x in range(12):
            if not killer.kill_now:
                time.sleep(5)
