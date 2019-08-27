import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import CounterMetricFamily

from collector.utils import add_gauge_metrics
from device import AbstractDevice

field_port = 0
field_counter_name = 1
field_rx_frames = 2
field_rx_bytes = 3
field_tx_frames = 4
field_tx_bytes = 5
field_rx_frames_by_size = 6
field_rx_bytes_by_size = 7
field_tx_frames_by_size = 8
field_tx_bytes_by_size = 9

field_thread_id = 0
field_thread_name = 1
field_error_count = 2
field_node = 3
field_error_reason = 4
field_index = 5


class VppctlShowErrorsCollector(object):
    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        template = open(template_dir + "/vppctl_show_errors_verbose.template",
                        "r")
        self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show errors verbose"')
        rows = self._parser.ParseText(output)

        if len(rows) == 0:
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
            thread_id = row[field_thread_id]
            thread_name = row[field_thread_name]
            for node, reason, index, count in zip(
                row[field_node], row[field_error_reason], row[field_index],
                row[field_error_count]):
                add_gauge_metrics(thread_err_count_metrics,
                                  [thread_id, thread_name, node, reason,
                                   index], float(count))

        total_err_count_metrics = metrics[1]
        row = rows[-1]
        for node, reason, index, count in zip(
            row[field_node], row[field_error_reason], row[field_index],
            row[field_error_count]):
            add_gauge_metrics(total_err_count_metrics, [node, reason, index],
                              float(count))
        return metrics
