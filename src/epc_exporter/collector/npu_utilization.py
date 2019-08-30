"""
Collects show npu utilization table command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.core import GaugeMetricFamily

from collector.abstract_command_collector import AbstractCommandCollector
from device import AbstractDevice


class NPUUtilizationCollector(AbstractCommandCollector):
    """ Collector for show npu utilization table command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(template_dir + "/show_npu_utilization_table.template",
                         device, registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
        output = self._device.exec("show npu utilization table")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_npu_usage_current",
                              "epc npu current usage percent.",
                              labels=["npu"]),
            GaugeMetricFamily("epc_npu_usage_5m",
                              "epc npu 5m usage percent.",
                              labels=["npu"]),
            GaugeMetricFamily("epc_npu_usage_15m",
                              "epc npu 15m usage percent.",
                              labels=["npu"])
        ]

        for row in rows:
            for field_index in range(3):
                metrics[field_index].add_metric(labels=[row[0]],
                                                value=row[field_index + 1])

        return metrics
