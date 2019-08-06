import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily, HistogramMetricFamily
from prometheus_client.utils import INF, floatToGoString

from device import AbstractDevice

port = 0
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
        info = self._info(template_dir, device)

        self._metrics = [
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

        for i in info:
            port = i[0]

            '''Rx Frame counts'''
            self._add_gauge_metrics(self._metrics[0], [port, "unicast"], i[rx_unicast_frames])
            self._add_gauge_metrics(self._metrics[0], [port, "multicast"], i[rx_multicast_frames])
            self._add_gauge_metrics(self._metrics[0], [port, "broadcast"], i[rx_broadcast_frames])

            '''Rx bytes'''
            self._add_gauge_metrics(self._metrics[1], [port, "ok"], i[rx_bytes_ok])
            self._add_gauge_metrics(self._metrics[1], [port, "bad"], i[rx_bytes_bad])

            '''Rx frame status by size'''
            self._add_gauge_metrics(self._metrics[2], [port, "short", "ok"], i[rx_short_ok])
            self._add_gauge_metrics(self._metrics[2], [port, "short", "crc"], i[rx_short_crc])
            self._add_gauge_metrics(self._metrics[2], [port, "norm", "ovf"], i[rx_ovf])
            self._add_gauge_metrics(self._metrics[2], [port, "norm", "crc"], i[rx_norm_crc])
            self._add_gauge_metrics(self._metrics[2], [port, "long", "ok"], i[rx_long_ok])
            self._add_gauge_metrics(self._metrics[2], [port, "long", "crc"], i[rx_long_crc])

            '''Rx Pause'''
            self._add_gauge_metrics(self._metrics[3], [port], i[rx_pause])

            '''Rx False CRS'''
            self._add_gauge_metrics(self._metrics[4], [port], i[rx_false_crs])

            '''Rx SYM Err'''
            self._add_gauge_metrics(self._metrics[5], [port], i[rx_sym_err])

            '''Rx Frames By Size'''
            self._add_histogram_metrics(self._metrics[6], [port], _upper_bounds, i[rx_frames_by_size], i[rx_bytes_ok])

            '''Tx Frame counts'''
            self._add_gauge_metrics(self._metrics[7], [port, "unicast"], i[tx_unicast_frames])
            self._add_gauge_metrics(self._metrics[7], [port, "multicast"], i[tx_multicast_frames])
            self._add_gauge_metrics(self._metrics[7], [port, "broadcast"], i[tx_broadcast_frames])

            '''Tx bytes'''
            self._add_gauge_metrics(self._metrics[8], [port, "ok"], i[tx_bytes_ok])
            self._add_gauge_metrics(self._metrics[8], [port, "bad"], i[tx_bytes_bad])

            '''Tx Pause'''
            self._add_gauge_metrics(self._metrics[9], [port], i[tx_pause])

            '''Tx Err'''
            self._add_gauge_metrics(self._metrics[10], [port], i[tx_err])

            '''Tx Frames By Size'''
            self._add_histogram_metrics(self._metrics[11], [port], _upper_bounds, i[tx_frames_by_size], i[tx_bytes_ok])

        if registry:
            registry.register(self)

    def collect(self):
        return self._metrics

    def _add_gauge_metrics(self, metric, labels, value):
        if value != "n/a":
            metric.add_metric(labels=labels, value=value)

    def _add_histogram_metrics(self, metric, labels, upper_bounds, values, sum_value):
        if values[0] != "n/a":
            buckets = []
            acc = 0
            for index, bound in enumerate(upper_bounds):
                acc += float(values[index])
                buckets.append([floatToGoString(bound), acc])

            metric.add_metric(labels=labels, buckets=buckets, sum_value=sum_value)

    def _info(self, template_dir: str, device: AbstractDevice):
        template = open(template_dir + "/show_port_datalink_counters.template", "r")

        re_table = textfsm.TextFSM(template)

        output = device.exec("show port datalink counters")
        return re_table.ParseText(output)
