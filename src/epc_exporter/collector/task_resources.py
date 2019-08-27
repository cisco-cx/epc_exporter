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
field_total_process_count = 9
field_total_cpu_usage = 10
field_total_mem_usage = 11
field_total_files_usage = 12


class TaskResourceCollector(object):
    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        template = open(template_dir + "/show_task_resources.template", "r")
        self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        output = self._device.exec("show task resources")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_task_cpu_used_percent",
                              "task cpu used percent",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_cpu_alloc_percent",
                              "task cpu used percent",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_memory_used_bytes",
                              "task memory used",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_memory_alloc_bytes",
                              "task memory allocated",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_files_used",
                              "task files used",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_files_alloc",
                              "task files allocated",
                              labels=["cpu", "facility", "instance"]),
            GaugeMetricFamily("epc_task_total_processes_count",
                              "total task process count"),
            GaugeMetricFamily("epc_task_total_cpu_used_percent",
                              "total task cpu usage in percent"),
            GaugeMetricFamily("epc_task_total_mem_used_bytes",
                              "total task memory usage in bytes"),
            GaugeMetricFamily("epc_task_total_files_used",
                              "total task files used"),
        ]

        for row in rows[:-1]:
            if row[field_cpu] == '':
                continue
            labels = [row[field_cpu], row[field_facility], row[field_instance]]
            add_gauge_metrics(metrics[0], labels,
                              parse_percent(row[field_cpu_used]))
            add_gauge_metrics(metrics[1], labels,
                              parse_percent(row[field_cpu_alloc]))
            add_gauge_metrics(metrics[2], labels,
                              parse_size(row[field_mem_used]))
            add_gauge_metrics(metrics[3], labels,
                              parse_size(row[field_mem_alloc]))
            add_gauge_metrics(metrics[4], labels,
                              parse_float(row[field_files_used]))
            add_gauge_metrics(metrics[5], labels,
                              parse_float(row[field_files_alloc]))

        if len(rows) > 0:
            add_gauge_metrics(metrics[6], [],
                              parse_float(rows[-1][field_total_process_count]))
            add_gauge_metrics(metrics[7], [],
                              parse_percent(rows[-1][field_total_cpu_usage]))
            add_gauge_metrics(metrics[8], [],
                              parse_size(rows[-1][field_total_mem_usage]))
            add_gauge_metrics(metrics[9], [],
                              parse_float(rows[-1][field_total_files_usage]))
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
