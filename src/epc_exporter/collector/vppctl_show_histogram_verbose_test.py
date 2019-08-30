import unittest

from prometheus_client import CollectorRegistry

from collector.vppctl_show_histogram_verbose import (
    VppctlShowHistogramVerboseCollector)
from device import TestDevice


class VppCtlShowHistogramVerboseTestCase(unittest.TestCase):
    def test_parsing(self):
        registry = CollectorRegistry()
        collector = VppctlShowHistogramVerboseCollector(
            "templates", TestDevice("test/data"), registry)

        collector.collect()


if __name__ == '__main__':
    unittest.main()
