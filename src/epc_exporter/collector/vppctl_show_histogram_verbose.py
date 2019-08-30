"""
Collects vppctl "show histogram verbose" command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import HistogramMetricFamily
from prometheus_client.utils import INF, floatToGoString

from collector.abstract_command_collector import AbstractCommandCollector
from device import AbstractDevice

FIELD_DATA_SET = 0
FIELD_PROCESS = 1
FIELD_INDEX = 2
FIELD_SYMBOL = 3
FIELD_BUCKET = 4
FIELD_BUCKET_UNIT = 5
FIELD_BUCKET_SAMPLES = 6
FIELD_BUCKET_SAMPLE_TIME = 7
FIELD_BUCKET_TOTAL_VALUE = 8
FIELD_BUCKET_VALUE_PER_SAMPLE = 9
FIELD_TOTAL_DT = 10
FIELD_TOTAL_DT_UNIT = 11
FIELD_MIN_DT = 12
FIELD_MIN_DT_UNIT = 13
FIELD_MAX_DT = 14
FIELD_MAX_DT_UNIT = 15
FIELD_TOTAL_VALUE = 16
FIELD_MIN_VALUE = 17
FIELD_MAX_VALUE = 18

_TIME_MULTIPLIER = {'cl': 1 / 10**10,
                    'ns': 1 / 10**9,
                    'us': 1 / 10**6,
                    'ms': 1 / 10**3,
                    's': 1,
                    'm': 60,
                    'h': 60 * 60,
                    'd': 60 * 60 * 24}


class VppctlShowHistogramVerboseCollector(AbstractCommandCollector):
    """ Collector for vppctl "show histogram verbose" command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(
            template_dir + "/vppctl_show_histogram_verbose.template", device,
            registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show histogram verbose"')
        rows = self._parser.ParseText(output)

        if not rows:
            return []

        histogram_metrics = HistogramMetricFamily(
            "epc_vppctl_performance",
            "vppctl performance metrics.",
            labels=["dataset", "process", "index"])

        for row in rows:
            buckets = []
            sample_acc = 0
            for b_symbol, bucket, b_unit, samples in zip(
                    row[FIELD_SYMBOL], row[FIELD_BUCKET],
                    row[FIELD_BUCKET_UNIT], row[FIELD_BUCKET_SAMPLES]):
                if b_symbol == '>':
                    bucket = INF
                elif b_symbol == '<':
                    bucket = float(bucket) - 0.1
                else:
                    bucket = float(bucket)
                sample_acc += float(samples)
                buckets.append([floatToGoString(bucket * _TIME_MULTIPLIER[
                    b_unit]), sample_acc])

            histogram_metrics.add_metric(
                labels=[row[FIELD_DATA_SET], row[FIELD_PROCESS], row[
                    FIELD_INDEX]],
                buckets=buckets,
                sum_value=(float(row[FIELD_TOTAL_DT]) * _TIME_MULTIPLIER[row[
                    FIELD_TOTAL_DT_UNIT]]))

        return [histogram_metrics]
