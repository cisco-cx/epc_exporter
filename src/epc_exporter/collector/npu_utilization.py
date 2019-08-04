import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from device import AbstractDevice


class NPUUtilizationCollector(object):
    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        info = self._info(template_dir, device)
        self._metrics = [
            GaugeMetricFamily("epc_npu_usage_current", "epc npu current usage percent.", labels=["npu"]),
            GaugeMetricFamily("epc_npu_usage_5m", "epc npu 5m usage percent.", labels=["npu"]),
            GaugeMetricFamily("epc_npu_usage_15m", "epc npu 15m usage percent.", labels=["npu"])
        ]

        for i in info:
            for fi in range(3):
                self._metrics[fi].add_metric(labels=[i[0]], value=i[fi + 1])

        if registry:
            registry.register(self)

    def collect(self):
        return self._metrics

    def _info(self, template_dir: str, device: AbstractDevice):
        template = open(template_dir + "/show_npu_utilization_table.template", "r")

        re_table = textfsm.TextFSM(template)

        output = device.exec("show npu utilization table")
        return re_table.ParseText(output)
