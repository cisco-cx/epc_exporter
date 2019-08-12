import os
import signal
import sys
import time

from prometheus_client import REGISTRY, write_to_textfile

from collector import *
from device import RemoteDevice, TestDevice


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
    output_path = sys.argv[2]

    killer = GracefulKiller()

    file_device = os.environ['FILE_DEVICE']

    if file_device == "":
        device = RemoteDevice(os.environ['DEVICE_HOSTNAME'], os.environ["DEVICE_USERNAME"],
                              os.environ["DEVICE_PASSWORD"], os.environ["TEST_PASSWORD"])
    else:
        device = TestDevice(file_device)

    NPUUtilizationCollector(templates_path, device)
    PortUtilizationCollector(templates_path, device)
    PortDataLinkCounterCollector(templates_path, device)
    PortNPUCounterCollector(templates_path, device)
    TaskResourceCollector(templates_path, device)
    VppctlShowErrorsCollector(templates_path, device)
    VppctlShowHistogramVerboseCollector(templates_path, device)

    while not killer.kill_now:
        device.start_session()
        write_to_textfile(output_path, REGISTRY)
        device.stop_session()

        for x in range(12):
            if not killer.kill_now:
                time.sleep(5)
