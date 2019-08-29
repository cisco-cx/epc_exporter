"""
Collects vppctl "show errors verbose" command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import CounterMetricFamily

from collector.abstract_command_collector import AbstractCommandCollector
from collector.utils import add_gauge_metrics
from device import AbstractDevice

FIELD_THREAD_ID = 0
FIELD_THREAD_NAME = 1
FIELD_ERROR_COUNT = 2
FIELD_NODE = 3
FIELD_ERROR_REASON = 4
FIELD_INDEX = 5


class VppctlShowErrorsCollector(AbstractCommandCollector):
    """ Collector for vppctl "show errors verbose" command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(template_dir + "/vppctl_show_errors_verbose.template",
                         device, registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show errors verbose"')
        rows = self._parser.ParseText(output)

        if not rows:
            return []

        metrics = [
            CounterMetricFamily(
                "epc_vppctl_thread_errors_count",
                "vppctl error counts by thread.",
                labels=["thread", "function", "node", "reason", "index"]),
            CounterMetricFamily("epc_vppctl_total_errors_count",
                                "vppctl total error counts.",
                                labels=["node", "reason", "index"])
        ]

        thread_err_count_metrics = metrics[0]
        for row in rows[:-1]:
            thread_id = row[FIELD_THREAD_ID]
            thread_name = row[FIELD_THREAD_NAME]
            for node, reason, index, count in zip(
                    row[FIELD_NODE], row[FIELD_ERROR_REASON], row[FIELD_INDEX],
                    row[FIELD_ERROR_COUNT]):
                add_gauge_metrics(thread_err_count_metrics,
                                  [thread_id, thread_name, node, reason,
                                   index], float(count))

        total_err_count_metrics = metrics[1]
        row = rows[-1]
        for node, reason, index, count in zip(
                row[FIELD_NODE], row[FIELD_ERROR_REASON], row[FIELD_INDEX],
                row[FIELD_ERROR_COUNT]):
            add_gauge_metrics(total_err_count_metrics, [node, reason, index],
                              float(count))
        return metrics
