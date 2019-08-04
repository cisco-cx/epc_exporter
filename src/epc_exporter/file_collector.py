import signal
import sys
import time

from prometheus_client import CollectorRegistry, write_to_textfile

from collector import TestCollector, NPUUtilizationCollector, PortUtilizationCollector


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

    while not killer.kill_now:
        registry = CollectorRegistry()
        TestCollector(registry)
        NPUUtilizationCollector(templates_path, test_data_path, registry)
        PortUtilizationCollector(templates_path, test_data_path, registry)
        write_to_textfile(output_path, registry)
        for x in range(12):
            if not killer.kill_now:
                time.sleep(5)
