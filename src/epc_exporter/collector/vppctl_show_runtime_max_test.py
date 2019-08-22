import unittest

from prometheus_client import CollectorRegistry

from collector.vppctl_show_runtime_max import VppctlShowRuntimeMaxCollector
from device import TestDevice


class VppctlShowRuntimeMaxTestCase(unittest.TestCase):
    def test_parsing(self):
        registry = CollectorRegistry()
        collector = VppctlShowRuntimeMaxCollector("templates", TestDevice("test/data"), registry)

        collector.collect()


if __name__ == '__main__':
    unittest.main()
