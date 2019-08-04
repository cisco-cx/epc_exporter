import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily


class NPUUtilizationCollector(object):
    def __init__(self, template_dir: str, data_dir: str, registry=REGISTRY):
        info = self._info(template_dir, data_dir)
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

    def _info(self, template_dir: str, data_dir: str):
        template = open(template_dir + "/show_npu_utilization_table.template", "r")

        re_table = textfsm.TextFSM(template)

        with open(data_dir + "/show_npu_utilization_table.txt", 'r') as file:
            cli_output = file.read()
            data = re_table.ParseText(cli_output)
        return data
