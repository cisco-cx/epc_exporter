import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.utils import add_gauge_metrics
from device import AbstractDevice

field_cpu = 0
field_facility = 1
field_instance = 2
field_cpu_used = 3
field_cpu_alloc = 4
field_mem_used = 5
field_mem_alloc = 6
field_files_used = 7
field_files_alloc = 8


class TaskResourceCollector(object):

    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        template = open(template_dir + "/show_task_resources.template", "r")
        self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        output = self._device.exec("show task resources")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_task_cpu_used", "task cpu used percent",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_cpu_alloc", "task cpu used percent",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_memory_used", "task memory used",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_memory_alloc", "task memory allocated",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_files_used", "task files used",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_files_alloc", "task files allocated",
                              labels=["cpu", "facility", "instance"]),
        ]

        for row in rows:
            labels = [row[field_cpu], row[field_facility], row[field_instance]]
            add_gauge_metrics(metrics[0], labels, parse_percent(row[field_cpu_used]))
            add_gauge_metrics(metrics[1], labels, parse_percent(row[field_cpu_alloc]))
            add_gauge_metrics(metrics[2], labels, parse_size(row[field_mem_used]))
            add_gauge_metrics(metrics[3], labels, parse_size(row[field_mem_alloc]))
            add_gauge_metrics(metrics[4], labels, parse_float(row[field_files_used]))
            add_gauge_metrics(metrics[5], labels, parse_float(row[field_files_alloc]))
        return metrics


units = {"B": 1, "K": 10 ** 3, "M": 10 ** 6, "G": 10 ** 9, "T": 10 ** 12}


def parse_size(size):
    if size == '--':
        return 0
    number = size[:-1]
    unit = size[-1]
    return int(float(number) * units[unit])


def parse_percent(size):
    if size == '--':
        return 0
    number = size[:-1]
    return float(number) / 100


def parse_float(val):
    if val == '--':
        return 0
    return float(val)
