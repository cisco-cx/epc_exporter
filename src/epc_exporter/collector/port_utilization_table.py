import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily


class PortUtilizationCollector(object):

    def __init__(self, template_dir: str, data_dir: str, registry=REGISTRY):
        info = self._info(template_dir, data_dir)

        self._metrics = [
            GaugeMetricFamily("epc_port_rx_1", "epc port rx 1m.", labels=["port"]),
            GaugeMetricFamily("epc_port_tx_1", "epc npu tx 1m.", labels=["port"]),
            GaugeMetricFamily("epc_port_rx_5", "epc port rx 5m.", labels=["port"]),
            GaugeMetricFamily("epc_port_tx_5", "epc npu tx 5m.", labels=["port"]),
            GaugeMetricFamily("epc_port_rx_15", "epc port rx 15m.", labels=["port"]),
            GaugeMetricFamily("epc_port_tx_15", "epc npu tx 15m.", labels=["port"])
        ]

        for i in info:
            self._metrics[0].add_metric(labels=[i[0]], value=i[1])
            self._metrics[1].add_metric(labels=[i[0]], value=i[2])
            self._metrics[2].add_metric(labels=[i[0]], value=i[3])
            self._metrics[3].add_metric(labels=[i[0]], value=i[4])
            self._metrics[4].add_metric(labels=[i[0]], value=i[5])
            self._metrics[5].add_metric(labels=[i[0]], value=i[6])

        if registry:
            registry.register(self)

    def collect(self):
        return self._metrics

    def _info(self, template_dir: str, data_dir: str):
        template = open(template_dir + "/show_port_utilization_table.template", "r")

        re_table = textfsm.TextFSM(template)

        with open(data_dir + "/show_port_utilization_table.txt", 'r') as file:
            cli_output = file.read()
            data = re_table.ParseText(cli_output)
        return data
