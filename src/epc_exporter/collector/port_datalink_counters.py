import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily, HistogramMetricFamily
from prometheus_client.utils import INF, floatToGoString

from device import AbstractDevice

field_port = 0
rx_unicast_frames = 1
rx_multicast_frames = 2
rx_broadcast_frames = 3
rx_bytes_ok = 4
rx_bytes_bad = 5
rx_short_ok = 6
rx_short_crc = 7
rx_ovf = 8
rx_norm_crc = 9
rx_long_ok = 10
rx_long_crc = 11
rx_pause = 12
rx_false_crs = 13
rx_sym_err = 14
rx_frames_by_size = 15
tx_unicast_frames = 16
tx_multicast_frames = 17
tx_broadcast_frames = 18
tx_bytes_ok = 19
tx_bytes_bad = 20
tx_pause = 21
tx_err = 22
tx_frames_by_size = 23

_upper_bounds = [64, 127, 255, 511, 1023, 1522, INF]


class PortDataLinkCounterCollector(object):

    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        template = open(template_dir + "/show_port_datalink_counters.template", "r")
        self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        output = self._device.exec("show port datalink counters")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_port_rx_frames_count", "The number of frames received.",
                              labels=["port", "type"]),
            GaugeMetricFamily("epc_port_rx_bytes_count", "The number of bytes that were received.",
                              labels=["port", "status"]),
            GaugeMetricFamily("epc_port_rx_frames_status_count", "The number of frames received with status.",
                              labels=["port", "size", "status"]),
            GaugeMetricFamily("epc_port_rx_pause", "The number of correct received flow-control frames.",
                              labels=["port"]),
            GaugeMetricFamily("epc_port_rx_false_crs", "The number of false carrier events detected.",
                              labels=["port"]),
            GaugeMetricFamily("epc_port_rx_sym_err",
                              "The number of received frames during which physical (PHY) symbol errors were detected.",
                              labels=["port"]),

            HistogramMetricFamily("epc_port_rx_frames_by_size",
                                  "The number of times that data was received according to "
                                  "number of frames that comprised it.", labels=["port"]),

            GaugeMetricFamily("epc_port_tx_frames_count", "The number of frames transmitted.",
                              labels=["port", "type"]),
            GaugeMetricFamily("epc_port_tx_bytes_count", "The number of bytes that were transmitted.",
                              labels=["port", "status"]),
            GaugeMetricFamily("epc_port_tx_pause", "The number of correct transmitted flow-control frames.",
                              labels=["port"]),
            GaugeMetricFamily("epc_port_tx_pause", "The number of correct transmitted flow-control frames.",
                              labels=["port"]),
            GaugeMetricFamily("epc_port_tx_err",
                              "The number of frames transmitted with an error due to transmit FIFO underflow or TXERR signal assertion.",
                              labels=["port"]),

            HistogramMetricFamily("epc_port_tx_frames_by_size",
                                  "The number of times that data was transmitted according to "
                                  "number of frames that comprised it.", labels=["port"])
        ]

        for row in rows:
            port = row[field_port]

            '''Rx Frame counts'''
            add_gauge_metrics(metrics[0], [port, "unicast"], row[rx_unicast_frames])
            add_gauge_metrics(metrics[0], [port, "multicast"], row[rx_multicast_frames])
            add_gauge_metrics(metrics[0], [port, "broadcast"], row[rx_broadcast_frames])

            '''Rx bytes'''
            add_gauge_metrics(metrics[1], [port, "ok"], row[rx_bytes_ok])
            add_gauge_metrics(metrics[1], [port, "bad"], row[rx_bytes_bad])

            '''Rx frame status by size'''
            add_gauge_metrics(metrics[2], [port, "short", "ok"], row[rx_short_ok])
            add_gauge_metrics(metrics[2], [port, "short", "crc"], row[rx_short_crc])
            add_gauge_metrics(metrics[2], [port, "norm", "ovf"], row[rx_ovf])
            add_gauge_metrics(metrics[2], [port, "norm", "crc"], row[rx_norm_crc])
            add_gauge_metrics(metrics[2], [port, "long", "ok"], row[rx_long_ok])
            add_gauge_metrics(metrics[2], [port, "long", "crc"], row[rx_long_crc])

            '''Rx Pause'''
            add_gauge_metrics(metrics[3], [port], row[rx_pause])

            '''Rx False CRS'''
            add_gauge_metrics(metrics[4], [port], row[rx_false_crs])

            '''Rx SYM Err'''
            add_gauge_metrics(metrics[5], [port], row[rx_sym_err])

            '''Rx Frames By Size'''
            add_histogram_metrics(metrics[6], [port], _upper_bounds, row[rx_frames_by_size], row[rx_bytes_ok])

            '''Tx Frame counts'''
            add_gauge_metrics(metrics[7], [port, "unicast"], row[tx_unicast_frames])
            add_gauge_metrics(metrics[7], [port, "multicast"], row[tx_multicast_frames])
            add_gauge_metrics(metrics[7], [port, "broadcast"], row[tx_broadcast_frames])

            '''Tx bytes'''
            add_gauge_metrics(metrics[8], [port, "ok"], row[tx_bytes_ok])
            add_gauge_metrics(metrics[8], [port, "bad"], row[tx_bytes_bad])

            '''Tx Pause'''
            add_gauge_metrics(metrics[9], [port], row[tx_pause])

            '''Tx Err'''
            add_gauge_metrics(metrics[10], [port], row[tx_err])

            '''Tx Frames By Size'''
            add_histogram_metrics(metrics[11], [port], _upper_bounds, row[tx_frames_by_size], row[tx_bytes_ok])

        return metrics


def add_gauge_metrics(metric, labels, value):
    if value != "n/a":
        metric.add_metric(labels=labels, value=value)


def add_histogram_metrics(metric, labels, upper_bounds, values, sum_value):
    if values[0] != "n/a":
        buckets = []
        acc = 0
        for index, bound in enumerate(upper_bounds):
            acc += float(values[index])
            buckets.append([floatToGoString(bound), acc])

        metric.add_metric(labels=labels, buckets=buckets, sum_value=sum_value)
