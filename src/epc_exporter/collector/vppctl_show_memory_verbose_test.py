import unittest

from prometheus_client import CollectorRegistry

from collector.vppctl_show_memory_verbose import VppctlShowMemoryVerboseCollector
from device import TestDevice


class VppctlShowMemoryVerboseTestCase(unittest.TestCase):
    def test_parsing(self):
        registry = CollectorRegistry()
        collector = VppctlShowMemoryVerboseCollector("templates", TestDevice("test/data"), registry)

        collector.collect()


if __name__ == '__main__':
    unittest.main()
