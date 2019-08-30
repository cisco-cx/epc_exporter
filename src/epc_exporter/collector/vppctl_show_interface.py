"""
Collects vppctl "show interface" command and parses it
"""

from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.abstract_command_collector import AbstractCommandCollector
from collector.utils import add_gauge_metrics
from device import AbstractDevice

FIELD_INTERFACE = 0
FIELD_STATE = 1
FIELD_MTU_L3 = 2
FIELD_MTU_IP4 = 3
FIELD_MTU_IP6 = 4
FIELD_MTU_MPLS = 5
FIELD_COUNTER_NAME = 6
FIELD_COUNTER_VALUE = 7


class VppctlShowInterfaceCollector(AbstractCommandCollector):
    """ Collector for vppctl "show interface" command """

    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        super().__init__(template_dir + "/vppctl_show_interface.template",
                         device, registry)

    def collect(self):
        """
        collect method collects the command output from device and
        return the metrics
        """
        self._device.enable_test_commands()
        output = self._device.exec('vppctl "show interface"')
        rows = self._parser.ParseText(output)

        metrics = [
            GaugeMetricFamily("epc_vppctl_interface_status",
                              "interface up or down",
                              labels=["interface"]),
            GaugeMetricFamily("epc_vppctl_interface_mtu",
                              "MTU value",
                              labels=["interface", "protocol"]),
            GaugeMetricFamily("epc_vppctl_interface_counter",
                              "interface counters and values",
                              labels=["interface", "name"]),
        ]

        for row in rows:
            interface = row[FIELD_INTERFACE]
            add_gauge_metrics(metrics[0], [interface], 1 if
                              row[FIELD_STATE] == "up" else 0)
            add_gauge_metrics(metrics[1], [interface, "l3"],
                              float(row[FIELD_MTU_L3]))
            add_gauge_metrics(metrics[1], [interface, "ip4"],
                              float(row[FIELD_MTU_IP4]))
            add_gauge_metrics(metrics[1], [interface, "ip6"],
                              float(row[FIELD_MTU_IP6]))
            add_gauge_metrics(metrics[1], [interface, "mpls"],
                              float(row[FIELD_MTU_MPLS]))
            for name, value in zip(row[FIELD_COUNTER_NAME],
                                   row[FIELD_COUNTER_VALUE]):
                add_gauge_metrics(metrics[2], [interface, name], float(value))
        return metrics
