import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.utils import add_gauge_metrics
from device import AbstractDevice

field_thread_id = 0
field_thread_name = 1
field_name = 2
field_max_node_clocks = 3
field_vectors_at_max = 4
field_max_clocks = 5
field_avg_clocks = 6
field_avg_vectors_per_clock = 7


class VppctlShowRuntimeMaxCollector(object):

    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        with open(template_dir + "/vppctl_show_runtime_max.template", "r") as template:
            self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show runtime max"')
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_vppctl_runtime_max_node_clocks", "max node clocks by thread",
                              labels=["thread_id", "thread_name", "name"]),
            GaugeMetricFamily("epc_vppctl_runtime_vectors_at_max", "vectors at max by thread",
                              labels=["thread_id", "thread_name", "name"]),
            GaugeMetricFamily("epc_vppctl_runtime_max_clocks", "max clocks by thread",
                              labels=["thread_id", "thread_name", "name"]),
            GaugeMetricFamily("epc_vppctl_runtime_avg_clocks", "avg clocks by thread",
                              labels=["thread_id", "thread_name", "name"]),
            GaugeMetricFamily("epc_vppctl_runtime_avg_vectors_per_clock", "avg vector per clock by thread",
                              labels=["thread_id", "thread_name", "name"]),
        ]

        for row in rows:
            thread_id = row[field_thread_id]
            thread_name = row[field_thread_name]
            for name, max_node_clocks, vectors_at_max, max_clocks, avg_clocks, avg_vectors_per_clock in zip(
                    row[field_name], row[field_max_node_clocks],
                    row[field_vectors_at_max],
                    row[field_max_clocks], row[field_avg_clocks],
                    row[field_avg_vectors_per_clock]):
                add_gauge_metrics(metrics[0], [thread_id, thread_name, name], float(max_node_clocks))
                add_gauge_metrics(metrics[1], [thread_id, thread_name, name], float(vectors_at_max))
                add_gauge_metrics(metrics[2], [thread_id, thread_name, name], float(max_clocks))
                add_gauge_metrics(metrics[3], [thread_id, thread_name, name], float(avg_clocks))
                add_gauge_metrics(metrics[4], [thread_id, thread_name, name], float(avg_vectors_per_clock))
        return metrics
