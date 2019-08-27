import os
import signal
import sys
import time

from prometheus_client import REGISTRY, write_to_textfile

from collector import registerCollectors
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

    file_device = os.environ.get('FILE_DEVICE')
    if file_device is not None:
        device = TestDevice(file_device)
    else:
        device = RemoteDevice(
            os.environ['DEVICE_HOSTNAME'], os.environ["DEVICE_USERNAME"],
            os.environ["DEVICE_PASSWORD"], os.environ["TEST_PASSWORD"])

    freqEnv = os.environ.get('FREQ')
    if freqEnv is not None:
        freq_in_seconds = int(freqEnv)
    else:
        freq_in_seconds = 60

    registerCollectors(templates_path, device)

    while not killer.kill_now:
        device.start_session()
        write_to_textfile(output_path, REGISTRY)
        device.stop_session()

        for x in range(int(freq_in_seconds / 5)):
            if not killer.kill_now:
                time.sleep(5)
