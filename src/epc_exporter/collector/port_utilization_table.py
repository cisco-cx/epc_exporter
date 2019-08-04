import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from device import AbstractDevice


class PortUtilizationCollector(object):

    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        info = self._info(template_dir, device)

        self._metrics = [
            GaugeMetricFamily("epc_port_rx_current", "epc port rx current.", labels=["port"]),
            GaugeMetricFamily("epc_port_tx_current", "epc npu tx current.", labels=["port"]),
            GaugeMetricFamily("epc_port_rx_5m", "epc port rx 5m.", labels=["port"]),
            GaugeMetricFamily("epc_port_tx_5m", "epc npu tx 5m.", labels=["port"]),
            GaugeMetricFamily("epc_port_rx_15m", "epc port rx 15m.", labels=["port"]),
            GaugeMetricFamily("epc_port_tx_15m", "epc npu tx 15m.", labels=["port"])
        ]

        for i in info:
            for fi in range(6):
                self._metrics[fi].add_metric(labels=[i[0]], value=i[fi + 1])

        if registry:
            registry.register(self)

    def collect(self):
        return self._metrics

    def _info(self, template_dir: str, device: AbstractDevice):
        template = open(template_dir + "/show_port_utilization_table.template", "r")

        re_table = textfsm.TextFSM(template)

        output = device.exec("show port utilization table")
        return re_table.ParseText(output)
