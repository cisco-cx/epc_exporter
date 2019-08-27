import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.utils import add_gauge_metrics
from device import AbstractDevice

field_thread_id = 0
field_thread_name = 1
field_numa = 2
field_memory_total = 3
field_memory_used = 4
field_memory_free = 5


class VppctlShowMemoryVerboseCollector(object):
    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        with open(template_dir + "/vppctl_show_memory_verbose.template",
                  "r") as template:
            self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show memory verbose"')
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_vppctl_thread_numa",
                              "numa",
                              labels=["thread_id", "thread_name"]),
            GaugeMetricFamily("epc_vppctl_thread_memory_total_bytes",
                              "memory total bytes",
                              labels=["thread_id", "thread_name"]),
            GaugeMetricFamily("epc_vppctl_thread_memory_used_bytes",
                              "memory used bytes",
                              labels=["thread_id", "thread_name"]),
            GaugeMetricFamily("epc_vppctl_thread_memory_free_bytes",
                              "memory free bytes",
                              labels=["thread_id", "thread_name", "name"]),
        ]

        for row in rows:
            thread_id = row[field_thread_id]
            thread_name = row[field_thread_name]

            add_gauge_metrics(metrics[0], [thread_id, thread_name],
                              float(row[field_numa]))
            add_gauge_metrics(metrics[1], [thread_id, thread_name],
                              parse_size(row[field_memory_total]))
            add_gauge_metrics(metrics[2], [thread_id, thread_name],
                              parse_size(row[field_memory_used]))
            add_gauge_metrics(metrics[3], [thread_id, thread_name],
                              parse_size(row[field_memory_free]))
        return metrics


units = {"B": 1, "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3, "T": 1024 ** 4}


def parse_size(size):
    number = size[:-1]
    unit = size[-1]
    return int(float(number) * units[unit])
