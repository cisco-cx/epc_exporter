"""
Collects show port utilization table command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.abstract_command_collector import AbstractCommandCollector
from device import AbstractDevice


class PortUtilizationCollector(AbstractCommandCollector):
    """ Collector for show port utilization table command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(
            template_dir + "/show_port_utilization_table.template", device,
            registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
        output = self._device.exec("show port utilization table")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_port_rx_current",
                              "epc port rx current.",
                              labels=["port"]),
            GaugeMetricFamily("epc_port_tx_current",
                              "epc npu tx current.",
                              labels=["port"]),
            GaugeMetricFamily("epc_port_rx_5m",
                              "epc port rx 5m.",
                              labels=["port"]), GaugeMetricFamily(
                                  "epc_port_tx_5m",
                                  "epc npu tx 5m.",
                                  labels=["port"]), GaugeMetricFamily(
                                      "epc_port_rx_15m",
                                      "epc port rx 15m.",
                                      labels=["port"]), GaugeMetricFamily(
                                          "epc_port_tx_15m",
                                          "epc npu tx 15m.",
                                          labels=["port"])
        ]

        for row in rows:
            for field_index in range(6):
                metrics[field_index].add_metric(labels=[row[0]],
                                                value=row[field_index + 1])

        return metrics
