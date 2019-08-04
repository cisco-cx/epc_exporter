import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from device import AbstractDevice


class NPUUtilizationCollector(object):
    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        info = self._info(template_dir, device)
        self._metrics = [
            GaugeMetricFamily("epc_npu_usage1", "epc npu 1m usage percent.", labels=["npu"]),
            GaugeMetricFamily("epc_npu_usage5", "epc npu 5m usage percent.", labels=["npu"]),
            GaugeMetricFamily("epc_npu_usage15", "epc npu 15m usage percent.", labels=["npu"])
        ]

        for i in info:
            self._metrics[0].add_metric(labels=[i[0]], value=i[1])
            self._metrics[1].add_metric(labels=[i[0]], value=i[2])
            self._metrics[2].add_metric(labels=[i[0]], value=i[3])

        if registry:
            registry.register(self)

    def collect(self):
        return self._metrics

    def _info(self, template_dir: str, device: AbstractDevice):
        template = open(template_dir + "/show_npu_utilization_table.template", "r")

        re_table = textfsm.TextFSM(template)

        output = device.exec("show npu utilization table")
        return re_table.ParseText(output)
