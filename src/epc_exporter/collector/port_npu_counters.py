import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily, HistogramMetricFamily
from prometheus_client.utils import INF

from collector.utils import add_gauge_metrics, add_histogram_metrics
from device import AbstractDevice

field_port = 0
field_counter_name = 1
field_rx_frames = 2
field_rx_bytes = 3
field_tx_frames = 4
field_tx_bytes = 5
field_rx_frames_by_size = 6
field_rx_bytes_by_size = 7
field_tx_frames_by_size = 8
field_tx_bytes_by_size = 9

_upper_bounds = [63, 127, 255, 511, 1023, 2047, 4095, 8191, INF]


class PortNPUCounterCollector(object):

    def __init__(self, template_dir: str, device: AbstractDevice, registry=REGISTRY):
        template = open(template_dir + "/show_port_npu_counters.template", "r")
        self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
        output = self._device.exec("show port npu counters")
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_port_npu_counter", "port npu counters.",
                              labels=["port", "counter", "type"]),

            HistogramMetricFamily("epc_port_npu_counters_by_size",
                                  "epc_port_npu_counters_by_size", labels=["port", "type"])
        ]

        for row in rows:
            port = row[field_port]
            counter_metric = metrics[0]
            for counter, rx_frames, rx_bytes, tx_frames, tx_bytes in zip(row[field_counter_name], row[field_rx_frames],
                                                                         row[field_rx_bytes], row[field_tx_frames],
                                                                         row[field_tx_bytes]):
                add_gauge_metrics(counter_metric, [port, counter, "rx_frames"], rx_frames)
                add_gauge_metrics(counter_metric, [port, counter, "rx_bytes"], rx_bytes)
                add_gauge_metrics(counter_metric, [port, counter, "tx_frames"], tx_frames)
                add_gauge_metrics(counter_metric, [port, counter, "tx_bytes"], tx_bytes)

            add_histogram_metrics(metrics[1], [port, "rx_frames"], _upper_bounds, row[field_rx_frames_by_size],
                                  sum(map(int, row[field_rx_bytes_by_size])))
            add_histogram_metrics(metrics[1], [port, "tx_frames"], _upper_bounds, row[field_tx_frames_by_size],
                                  sum(map(int, row[field_tx_bytes_by_size])))
        return metrics
