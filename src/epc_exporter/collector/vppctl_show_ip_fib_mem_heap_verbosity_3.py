import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.utils import add_gauge_metrics
from device import AbstractDevice

field_memory_total = 0
field_memory_used = 1
field_memory_free = 2
field_vrf = 4


class VppctlShowIPFibMemHeapCollector(object):

    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        with open(template_dir + "/vppctl_show_ip_fib_mem_heap-verbosity_3.template", "r") as template:
            self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show ip fib mem heap-verbosity 3"')
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_vppctl_ip_fib_heap_memory_total_bytes", "ip fib heap memory total bytes"),
            GaugeMetricFamily("epc_vppctl_ip_fib_heap_memory_used_bytes", "ip fib heap memory used bytes"),
            GaugeMetricFamily("epc_vppctl_ip_fib_heap_memory_free_bytes", "ip fib heap memory free bytes"),
            GaugeMetricFamily("epc_vppctl_ip_fib_vrf_status", "ip fib vrf status", labels=["vrf"]),
        ]

        if len(rows) == 0:
            return metrics

        row = rows[0]
        add_gauge_metrics(metrics[0], [], parse_size(row[field_memory_total]))
        add_gauge_metrics(metrics[1], [], parse_size(row[field_memory_used]))
        add_gauge_metrics(metrics[2], [], parse_size(row[field_memory_free]))

        for vrf in row[field_vrf]:
            add_gauge_metrics(metrics[3], [vrf], 1)

        return metrics


units = {"B": 1, "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3, "T": 1024 ** 4}


def parse_size(size):
    number = size[:-1]
    unit = size[-1]
    return int(float(number) * units[unit])
