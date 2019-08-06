import textfsm
from prometheus_client import REGISTRY
from prometheus_client.core import GaugeMetricFamily

from device import AbstractDevice


class NPUUtilizationCollector(object):
    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        template = open(template_dir + "/show_npu_utilization_table.template", "r")
        self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        output = self._device.exec("show npu utilization table")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_npu_usage_current", "epc npu current usage percent.", labels=["npu"]),
            GaugeMetricFamily("epc_npu_usage_5m", "epc npu 5m usage percent.", labels=["npu"]),
            GaugeMetricFamily("epc_npu_usage_15m", "epc npu 15m usage percent.", labels=["npu"])
        ]

        for row in rows:
            for field_index in range(3):
                metrics[field_index].add_metric(labels=[row[0]], value=row[field_index + 1])

        return metrics
