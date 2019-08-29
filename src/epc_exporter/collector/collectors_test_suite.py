import unittest

from collector.vppctl_show_histogram_verbose_test import (
    VppCtlShowHistogramVerboseTestCase)
from collector.vppctl_show_ip_fib_mem_heap_verbosity_3_test import (
    VppctlShowIPFibMemHeapTestCase)
from collector.vppctl_show_memory_verbose_test import (
    VppctlShowMemoryVerboseTestCase)
from collector.vppctl_show_runtime_max_test import (
    VppctlShowRuntimeMaxTestCase)


def create_suite():
    test_suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    test_suite.addTest(loader.loadTestsFromTestCase(
        VppCtlShowHistogramVerboseTestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(
        VppctlShowIPFibMemHeapTestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(
        VppctlShowMemoryVerboseTestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(
        VppctlShowRuntimeMaxTestCase))
    return test_suite


if __name__ == '__main__':
    suite = create_suite()

    runner = unittest.TextTestRunner()
    runner.run(suite)
