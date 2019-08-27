import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import HistogramMetricFamily
from prometheus_client.utils import INF, floatToGoString

from device import AbstractDevice

field_data_set = 0
field_process = 1
field_index = 2
field_symbol = 3
field_bucket = 4
field_bucket_unit = 5
field_bucket_samples = 6
field_bucket_sample_time = 7
field_bucket_total_value = 8
field_bucket_value_per_sample = 9
field_total_dt = 10
field_total_dt_unit = 11
field_min_dt = 12
field_min_dt_unit = 13
field_max_dt = 14
field_max_dt_unit = 15
field_total_value = 16
field_min_value = 17
field_max_value = 18

_time_multiplier = {'cl': 1 / 10 ** 10,
                    'ns': 1 / 10 ** 9,
                    'us': 1 / 10 ** 6,
                    'ms': 1 / 10 ** 3,
                    's': 1,
                    'm': 60,
                    'h': 60 * 60,
                    'd': 60 * 60 * 24}


class VppctlShowHistogramVerboseCollector(object):
    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        with open(template_dir + "/vppctl_show_histogram_verbose.template",
                  "r") as template:
            self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show histogram verbose"')
        rows = self._parser.ParseText(output)

        if len(rows) == 0:
            return []

        histogramMetrics = HistogramMetricFamily(
            "epc_vppctl_performance",
            "vppctl performance metrics.",
            labels=["dataset", "process", "index"])

        for row in rows:
            buckets = []
            sample_acc = 0
            for bs, b, bu, samples in zip(row[field_symbol], row[field_bucket],
                                          row[field_bucket_unit],
                                          row[field_bucket_samples]):
                if bs == '>':
                    b = INF
                elif bs == '<':
                    b = float(b) - 0.1
                else:
                    b = float(b)
                sample_acc += float(samples)
                buckets.append([floatToGoString(b * _time_multiplier[bu]),
                                sample_acc])

            histogramMetrics.add_metric(
                labels=[row[field_data_set], row[field_process], row[
                    field_index]],
                buckets=buckets,
                sum_value=(float(row[field_total_dt]) * _time_multiplier[row[
                    field_total_dt_unit]]))

        return [histogramMetrics]
