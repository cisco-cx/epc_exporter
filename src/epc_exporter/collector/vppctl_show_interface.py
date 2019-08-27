import textfsm
from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily

from collector.utils import add_gauge_metrics
from device import AbstractDevice

field_interface = 0
field_state = 1
field_mtu_l3 = 2
field_mtu_ip4 = 3
field_mtu_ip6 = 4
field_mtu_mpls = 5
field_counter_name = 6
field_counter_value = 7


class VppctlShowInterfaceCollector(object):
    def __init__(self,
                 template_dir: str,
                 device: AbstractDevice,
                 registry=REGISTRY):
        with open(template_dir + "/vppctl_show_interface.template",
                  "r") as template:
            self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)

    def collect(self):
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
            interface = row[field_interface]
            add_gauge_metrics(metrics[0], [interface], 1 if
            row[field_state] == "up" else 0)
            add_gauge_metrics(metrics[1], [interface, "l3"],
                              float(row[field_mtu_l3]))
            add_gauge_metrics(metrics[1], [interface, "ip4"],
                              float(row[field_mtu_ip4]))
            add_gauge_metrics(metrics[1], [interface, "ip6"],
                              float(row[field_mtu_ip6]))
            add_gauge_metrics(metrics[1], [interface, "mpls"],
                              float(row[field_mtu_mpls]))
            for name, value in zip(row[field_counter_name],
                                   row[field_counter_value]):
                add_gauge_metrics(metrics[2], [interface, name], float(value))
        return metrics
