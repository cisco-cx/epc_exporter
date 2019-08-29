"""
Collects vppctl "show ip fib mem heap-verbosity 3" command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.abstract_command_collector import AbstractCommandCollector
from collector.utils import add_gauge_metrics, parse_size
from device import AbstractDevice

FIELD_MEMORY_TOTAL = 0
FIELD_MEMORY_USED = 1
FIELD_MEMORY_FREE = 2
FIELD_VRF = 4


class VppctlShowIPFibMemHeapCollector(AbstractCommandCollector):
    """ Collector for vppctl "show ip fib mem heap-verbosity 3" command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(
            template_dir + "/vppctl_show_ip_fib_mem_heap-verbosity_3.template",
            device, registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show ip fib mem heap-verbosity 3"')
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_vppctl_ip_fib_heap_memory_total_bytes",
                              "ip fib heap memory total bytes"),
            GaugeMetricFamily("epc_vppctl_ip_fib_heap_memory_used_bytes",
                              "ip fib heap memory used bytes"),
            GaugeMetricFamily("epc_vppctl_ip_fib_heap_memory_free_bytes",
                              "ip fib heap memory free bytes"),
            GaugeMetricFamily("epc_vppctl_ip_fib_vrf_status",
                              "ip fib vrf status",
                              labels=["vrf"]),
        ]

        if not rows:
            return metrics

        row = rows[0]
        add_gauge_metrics(metrics[0], [], parse_size(row[FIELD_MEMORY_TOTAL]))
        add_gauge_metrics(metrics[1], [], parse_size(row[FIELD_MEMORY_USED]))
        add_gauge_metrics(metrics[2], [], parse_size(row[FIELD_MEMORY_FREE]))

        for vrf in row[FIELD_VRF]:
            add_gauge_metrics(metrics[3], [vrf], 1)

        return metrics
