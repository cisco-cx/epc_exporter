"""
Collects vppctl "show runtime max" command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.abstract_command_collector import AbstractCommandCollector
from collector.utils import add_gauge_metrics
from device import AbstractDevice

FIELD_THREAD_ID = 0
FIELD_THREAD_NAME = 1
FIELD_NAME = 2
FIELD_MAX_NODE_CLOCKS = 3
FIELD_VECTORS_AT_MAX = 4
FIELD_MAX_CLOCKS = 5
FIELD_AVG_CLOCKS = 6
FIELD_AVG_VECTORS_PER_CLOCK = 7


class VppctlShowRuntimeMaxCollector(AbstractCommandCollector):
    """ Collector for vppctl "show runtime max" command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(template_dir + "/vppctl_show_runtime_max.template",
                         device, registry)

    def collect(self):
        """ collect method collects the command output from device and
            return the metrics
        """
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show runtime max"')
        rows = self._parser.ParseText(output)

        labels = ["thread_id", "thread_name", "name"]
        metrics = [
            GaugeMetricFamily("epc_vppctl_runtime_max_node_clocks",
                              "max node clocks by thread",
                              labels=labels),
            GaugeMetricFamily("epc_vppctl_runtime_vectors_at_max",
                              "vectors at max by thread",
                              labels=labels),
            GaugeMetricFamily("epc_vppctl_runtime_max_clocks",
                              "max clocks by thread",
                              labels=labels),
            GaugeMetricFamily("epc_vppctl_runtime_avg_clocks",
                              "avg clocks by thread",
                              labels=labels),
            GaugeMetricFamily("epc_vppctl_runtime_avg_vectors_per_clock",
                              "avg vector per clock by thread",
                              labels=labels),
        ]

        for row in rows:
            thread_id = row[FIELD_THREAD_ID]
            thread_name = row[FIELD_THREAD_NAME]
            for name, max_node_clocks, vectors_at_max, max_clocks, \
                avg_clocks, avg_vectors_per_clock in zip(
                        row[FIELD_NAME],
                        row[FIELD_MAX_NODE_CLOCKS],
                        row[FIELD_VECTORS_AT_MAX],
                        row[FIELD_MAX_CLOCKS],
                        row[FIELD_AVG_CLOCKS],
                        row[FIELD_AVG_VECTORS_PER_CLOCK]):
                add_gauge_metrics(metrics[0], [thread_id, thread_name, name],
                                  float(max_node_clocks))
                add_gauge_metrics(metrics[1], [thread_id, thread_name, name],
                                  float(vectors_at_max))
                add_gauge_metrics(metrics[2], [thread_id, thread_name, name],
                                  float(max_clocks))
                add_gauge_metrics(metrics[3], [thread_id, thread_name, name],
                                  float(avg_clocks))
                add_gauge_metrics(metrics[4], [thread_id, thread_name, name],
                                  float(avg_vectors_per_clock))
        return metrics
