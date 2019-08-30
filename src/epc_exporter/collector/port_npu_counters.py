"""
Collects show port npu counters command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import (GaugeMetricFamily,
                                            HistogramMetricFamily)
from prometheus_client.utils import INF

from collector.abstract_command_collector import AbstractCommandCollector
from collector.utils import add_gauge_metrics, add_histogram_metrics
from device import AbstractDevice

FIELD_PORT = 0
FIELD_COUNTER_NAME = 1
FIELD_RX_FRAMES = 2
FIELD_RX_BYTES = 3
FIELD_TX_FRAMES = 4
FIELD_TX_BYTES = 5
FIELD_RX_FRAMES_BY_SIZE = 6
FIELD_RX_BYTES_BY_SIZE = 7
FIELD_TX_FRAMES_BY_SIZE = 8
FIELD_TX_BYTES_BY_SIZE = 9

_UPPER_BOUNDS = [63, 127, 255, 511, 1023, 2047, 4095, 8191, INF]


class PortNPUCounterCollector(AbstractCommandCollector):
    """ Collector for show port npu counters command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(template_dir + "/show_port_npu_counters.template",
                         device, registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
        output = self._device.exec("show port npu counters")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_port_npu_counter",
                              "port npu counters.",
                              labels=["port", "counter", "type"]),
            HistogramMetricFamily("epc_port_npu_counters_by_size",
                                  "epc_port_npu_counters_by_size",
                                  labels=["port", "type"])
        ]

        for row in rows:
            port = row[FIELD_PORT]
            counter_metric = metrics[0]
            for counter, rx_frames, rx_bytes, tx_frames, tx_bytes in zip(
                    row[FIELD_COUNTER_NAME], row[FIELD_RX_FRAMES],
                    row[FIELD_RX_BYTES], row[FIELD_TX_FRAMES],
                    row[FIELD_TX_BYTES]):
                add_gauge_metrics(counter_metric, [port, counter, "rx_frames"],
                                  rx_frames)
                add_gauge_metrics(counter_metric, [port, counter, "rx_bytes"],
                                  rx_bytes)
                add_gauge_metrics(counter_metric, [port, counter, "tx_frames"],
                                  tx_frames)
                add_gauge_metrics(counter_metric, [port, counter, "tx_bytes"],
                                  tx_bytes)

            add_histogram_metrics(metrics[1], [port, "rx_frames"],
                                  _UPPER_BOUNDS, row[FIELD_RX_FRAMES_BY_SIZE],
                                  sum(map(int, row[FIELD_RX_BYTES_BY_SIZE])))
            add_histogram_metrics(metrics[1], [port, "tx_frames"],
                                  _UPPER_BOUNDS, row[FIELD_TX_FRAMES_BY_SIZE],
                                  sum(map(int, row[FIELD_TX_BYTES_BY_SIZE])))
        return metrics
