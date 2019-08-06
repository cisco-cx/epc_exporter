import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from device import AbstractDevice


class PortUtilizationCollector(object):

    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        template = open(template_dir + "/show_port_utilization_table.template", "r")

        self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):

        output = self._device.exec("show port utilization table")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_port_rx_current", "epc port rx current.", labels=["port"]),
            GaugeMetricFamily("epc_port_tx_current", "epc npu tx current.", labels=["port"]),
            GaugeMetricFamily("epc_port_rx_5m", "epc port rx 5m.", labels=["port"]),
            GaugeMetricFamily("epc_port_tx_5m", "epc npu tx 5m.", labels=["port"]),
            GaugeMetricFamily("epc_port_rx_15m", "epc port rx 15m.", labels=["port"]),
            GaugeMetricFamily("epc_port_tx_15m", "epc npu tx 15m.", labels=["port"])
        ]

        for row in rows:
            for fi in range(6):
                metrics[fi].add_metric(labels=[row[0]], value=row[fi + 1])

        return metrics
