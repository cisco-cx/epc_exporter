import unittest

from prometheus_client import CollectorRegistry

from collector.vppctl_show_ip_fib_mem_heap_verbosity_3 import (
    VppctlShowIPFibMemHeapCollector)
from device import TestDevice


class VppctlShowIPFibMemHeapTestCase(unittest.TestCase):
    def test_parsing(self):
        registry = CollectorRegistry()
        collector = VppctlShowIPFibMemHeapCollector(
            "templates", TestDevice("test/data"), registry)

        collector.collect()


if __name__ == '__main__':
    unittest.main()
