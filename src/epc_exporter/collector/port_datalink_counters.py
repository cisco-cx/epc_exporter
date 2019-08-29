"""
Collects show port datalink counters command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import (GaugeMetricFamily,
                                            HistogramMetricFamily)
from prometheus_client.utils import INF

from collector.abstract_command_collector import AbstractCommandCollector
from collector.utils import add_histogram_metrics, add_gauge_metrics
from device import AbstractDevice

FIELD_PORT = 0
RX_UNICAST_FRAMES = 1
RX_MULTICAST_FRAMES = 2
RX_BROADCAST_FRAMES = 3
RX_BYTES_OK = 4
RX_BYTES_BAD = 5
RX_SHORT_OK = 6
RX_SHORT_CRC = 7
RX_OVF = 8
RX_NORM_CRC = 9
RX_LONG_OK = 10
RX_LONG_CRC = 11
RX_PAUSE = 12
RX_FALSE_CRS = 13
RX_SYM_ERR = 14
RX_FRAMES_BY_SIZE = 15
TX_UNICAST_FRAMES = 16
TX_MULTICAST_FRAMES = 17
TX_BROADCAST_FRAMES = 18
TX_BYTES_OK = 19
TX_BYTES_BAD = 20
TX_PAUSE = 21
TX_ERR = 22
TX_FRAMES_BY_SIZE = 23

_UPPER_BOUNDS = [64, 127, 255, 511, 1023, 1522, INF]


class PortDataLinkCounterCollector(AbstractCommandCollector):
    """ Collector for show port datalink counters command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(
            template_dir + "/show_port_datalink_counters.template", device,
            registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
        output = self._device.exec("show port datalink counters")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_port_rx_frames_count",
                              "The number of frames received.",
                              labels=["port", "type"]), GaugeMetricFamily(
                                  "epc_port_rx_bytes_count",
                                  "The number of bytes that were received.",
                                  labels=["port", "status"]),
            GaugeMetricFamily(
                "epc_port_rx_frames_status_count",
                "The number of frames received with status.",
                labels=["port", "size", "status"]), GaugeMetricFamily(
                    "epc_port_rx_pause",
                    "The number of correct received flow-control frames.",
                    labels=["port"]), GaugeMetricFamily(
                        "epc_port_rx_false_crs",
                        "The number of false carrier events detected.",
                        labels=["port"]),
            GaugeMetricFamily(
                "epc_port_rx_sym_err",
                "The number of received frames during which physical (PHY)"
                " symbol errors were detected.",
                labels=["port"]), HistogramMetricFamily(
                    "epc_port_rx_frames_by_size",
                    "The number of times that data was received according to "
                    "number of frames that comprised it.",
                    labels=["port"]), GaugeMetricFamily(
                        "epc_port_tx_frames_count",
                        "The number of frames transmitted.",
                        labels=["port", "type"]),
            GaugeMetricFamily(
                "epc_port_tx_bytes_count",
                "The number of bytes that were transmitted.",
                labels=["port", "status"]), GaugeMetricFamily(
                    "epc_port_tx_pause",
                    "The number of correct transmitted flow-control frames.",
                    labels=["port"]), GaugeMetricFamily(
                        "epc_port_tx_err",
                        "The number of frames transmitted with an error due to"
                        " transmit FIFO underflow or TXERR signal assertion.",
                        labels=["port"]),
            HistogramMetricFamily(
                "epc_port_tx_frames_by_size",
                "The number of times that data was transmitted according to "
                "number of frames that comprised it.",
                labels=["port"])
        ]

        for row in rows:
            port = row[FIELD_PORT]
            # Rx Frame counts
            add_gauge_metrics(metrics[0], [port, "unicast"],
                              row[RX_UNICAST_FRAMES])
            add_gauge_metrics(metrics[0], [port, "multicast"],
                              row[RX_MULTICAST_FRAMES])
            add_gauge_metrics(metrics[0], [port, "broadcast"],
                              row[RX_BROADCAST_FRAMES])
            # Rx bytes
            add_gauge_metrics(metrics[1], [port, "ok"], row[RX_BYTES_OK])
            add_gauge_metrics(metrics[1], [port, "bad"], row[RX_BYTES_BAD])
            # Rx frame status by size
            add_gauge_metrics(metrics[2], [port, "short", "ok"],
                              row[RX_SHORT_OK])
            add_gauge_metrics(metrics[2], [port, "short", "crc"],
                              row[RX_SHORT_CRC])
            add_gauge_metrics(metrics[2], [port, "norm", "ovf"], row[RX_OVF])
            add_gauge_metrics(metrics[2], [port, "norm", "crc"],
                              row[RX_NORM_CRC])
            add_gauge_metrics(metrics[2], [port, "long", "ok"],
                              row[RX_LONG_OK])
            add_gauge_metrics(metrics[2], [port, "long", "crc"],
                              row[RX_LONG_CRC])
            # Rx Pause
            add_gauge_metrics(metrics[3], [port], row[RX_PAUSE])
            # Rx False CRS
            add_gauge_metrics(metrics[4], [port], row[RX_FALSE_CRS])
            # Rx SYM Err
            add_gauge_metrics(metrics[5], [port], row[RX_SYM_ERR])
            # Rx Frames By Size
            add_histogram_metrics(metrics[6], [port], _UPPER_BOUNDS,
                                  row[RX_FRAMES_BY_SIZE], row[RX_BYTES_OK])
            # Tx Frame counts
            add_gauge_metrics(metrics[7], [port, "unicast"],
                              row[TX_UNICAST_FRAMES])
            add_gauge_metrics(metrics[7], [port, "multicast"],
                              row[TX_MULTICAST_FRAMES])
            add_gauge_metrics(metrics[7], [port, "broadcast"],
                              row[TX_BROADCAST_FRAMES])
            # Tx bytes
            add_gauge_metrics(metrics[8], [port, "ok"], row[TX_BYTES_OK])
            add_gauge_metrics(metrics[8], [port, "bad"], row[TX_BYTES_BAD])
            # Tx Pause
            add_gauge_metrics(metrics[9], [port], row[TX_PAUSE])
            # Tx Err
            add_gauge_metrics(metrics[10], [port], row[TX_ERR])
            # Tx Frames By Size
            add_histogram_metrics(metrics[11], [port], _UPPER_BOUNDS,
                                  row[TX_FRAMES_BY_SIZE], row[TX_BYTES_OK])

        return metrics
