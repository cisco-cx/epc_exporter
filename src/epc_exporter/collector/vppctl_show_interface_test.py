import unittest

from prometheus_client import CollectorRegistry

from collector.vppctl_show_interface import VppctlShowInterfaceCollector
from device import TestDevice


class VppctlShowInterfaceTestCase(unittest.TestCase):
    def test_parsing(self):
        registry = CollectorRegistry()
        collector = VppctlShowInterfaceCollector("templates", TestDevice("test/data"), registry)

        collector.collect()


if __name__ == '__main__':
    unittest.main()
