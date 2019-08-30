"""
Collects show task resources command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.abstract_command_collector import AbstractCommandCollector
from collector.utils import add_gauge_metrics, parse_size
from device import AbstractDevice

FIELD_CPU = 0
FIELD_FACILITY = 1
FIELD_INSTANCE = 2
FIELD_CPU_USED = 3
FIELD_CPU_ALLOC = 4
FIELD_MEM_USED = 5
FIELD_MEM_ALLOC = 6
FIELD_FILES_USED = 7
FIELD_FILES_ALLOC = 8
FIELD_TOTAL_PROCESS_COUNT = 9
FIELD_TOTAL_CPU_USAGE = 10
FIELD_TOTAL_MEM_USAGE = 11
FIELD_TOTAL_FILES_USAGE = 12


class TaskResourceCollector(AbstractCommandCollector):
    """ Collector for show task resources command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(template_dir + "/show_task_resources.template",
                         device, registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
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
            if row[FIELD_CPU] == '':
                continue
            labels = [row[FIELD_CPU], row[FIELD_FACILITY], row[FIELD_INSTANCE]]
            add_gauge_metrics(metrics[0], labels,
                              parse_percent(row[FIELD_CPU_USED]))
            add_gauge_metrics(metrics[1], labels,
                              parse_percent(row[FIELD_CPU_ALLOC]))
            add_gauge_metrics(metrics[2], labels,
                              parse_size(row[FIELD_MEM_USED]))
            add_gauge_metrics(metrics[3], labels,
                              parse_size(row[FIELD_MEM_ALLOC]))
            add_gauge_metrics(metrics[4], labels,
                              parse_float(row[FIELD_FILES_USED]))
            add_gauge_metrics(metrics[5], labels,
                              parse_float(row[FIELD_FILES_ALLOC]))

        if rows:
            add_gauge_metrics(metrics[6], [],
                              parse_float(rows[-1][FIELD_TOTAL_PROCESS_COUNT]))
            add_gauge_metrics(metrics[7], [],
                              parse_percent(rows[-1][FIELD_TOTAL_CPU_USAGE]))
            add_gauge_metrics(metrics[8], [],
                              parse_size(rows[-1][FIELD_TOTAL_MEM_USAGE]))
            add_gauge_metrics(metrics[9], [],
                              parse_float(rows[-1][FIELD_TOTAL_FILES_USAGE]))
        return metrics


def parse_percent(size):
    """parses string percent value to float, ignores -- as 0"""
    if size == '--':
        return 0
    number = size[:-1]
    return float(number) / 100


def parse_float(val):
    """parses string as float, ignores -- as 0"""
    if val == '--':
        return 0
    return float(val)
