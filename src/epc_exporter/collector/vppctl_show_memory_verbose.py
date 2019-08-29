"""
Collects vppctl "show memory verbose" command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.abstract_command_collector import AbstractCommandCollector
from collector.utils import add_gauge_metrics, parse_size
from device import AbstractDevice

FIELD_THREAD_ID = 0
FIELD_THREAD_NAME = 1
FIELD_NUMA = 2
FIELD_MEMORY_TOTAL = 3
FIELD_MEMORY_USED = 4
FIELD_MEMORY_FREE = 5


class VppctlShowMemoryVerboseCollector(AbstractCommandCollector):
    """ Collector for vppctl "show memory verbose" command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(template_dir + "/vppctl_show_memory_verbose.template",
                         device, registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show memory verbose"')
        rows = self._parser.ParseText(output)

        labels = ["thread_id", "thread_name"]
        metrics = [
            GaugeMetricFamily("epc_vppctl_thread_numa",
                              "numa",
                              labels=labels),
            GaugeMetricFamily("epc_vppctl_thread_memory_total_bytes",
                              "memory total bytes",
                              labels=labels),
            GaugeMetricFamily("epc_vppctl_thread_memory_used_bytes",
                              "memory used bytes",
                              labels=labels),
            GaugeMetricFamily("epc_vppctl_thread_memory_free_bytes",
                              "memory free bytes",
                              labels=labels),
        ]

        for row in rows:
            thread_id = row[FIELD_THREAD_ID]
            thread_name = row[FIELD_THREAD_NAME]

            add_gauge_metrics(metrics[0], [thread_id, thread_name],
                              float(row[FIELD_NUMA]))
            add_gauge_metrics(metrics[1], [thread_id, thread_name],
                              parse_size(row[FIELD_MEMORY_TOTAL]))
            add_gauge_metrics(metrics[2], [thread_id, thread_name],
                              parse_size(row[FIELD_MEMORY_USED]))
            add_gauge_metrics(metrics[3], [thread_id, thread_name],
                              parse_size(row[FIELD_MEMORY_FREE]))
        return metrics
