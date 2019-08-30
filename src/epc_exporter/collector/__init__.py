"""
EPC collector module, collects the commands data from EPC and exposes them as
Prometheus collectors.
"""
from prometheus_client import REGISTRY

from device import AbstractDevice
from .npu_utilization import NPUUtilizationCollector
from .port_datalink_counters import PortDataLinkCounterCollector
from .port_npu_counters import PortNPUCounterCollector
from .port_utilization_table import PortUtilizationCollector
from .task_resources import TaskResourceCollector
from .vppctl_show_errors_verbose import VppctlShowErrorsCollector
from .vppctl_show_histogram_verbose import VppctlShowHistogramVerboseCollector
from .vppctl_show_interface import VppctlShowInterfaceCollector
from .vppctl_show_ip_fib_mem_heap_verbosity_3 import (
    VppctlShowIPFibMemHeapCollector)
from .vppctl_show_memory_verbose import VppctlShowMemoryVerboseCollector
from .vppctl_show_runtime_max import VppctlShowRuntimeMaxCollector

__all__ = ['NPUUtilizationCollector', 'PortDataLinkCounterCollector',
           'PortNPUCounterCollector', 'PortUtilizationCollector',
           'TaskResourceCollector', 'VppctlShowErrorsCollector',
           'VppctlShowHistogramVerboseCollector',
           'VppctlShowInterfaceCollector', 'VppctlShowIPFibMemHeapCollector',
           'VppctlShowMemoryVerboseCollector', 'VppctlShowRuntimeMaxCollector',
           'register_collectors']


def register_collectors(templates_path: str,
                        device: AbstractDevice,
                        registry=REGISTRY):
    """
    register all collectors with provided registry.
    Collectors will use device instance to collect the command output
    """
    NPUUtilizationCollector(templates_path, device, registry)
    PortUtilizationCollector(templates_path, device, registry)
    PortDataLinkCounterCollector(templates_path, device, registry)
    PortNPUCounterCollector(templates_path, device, registry)
    TaskResourceCollector(templates_path, device, registry)
    VppctlShowErrorsCollector(templates_path, device, registry)
    VppctlShowHistogramVerboseCollector(templates_path, device, registry)
    VppctlShowRuntimeMaxCollector(templates_path, device, registry)
    VppctlShowInterfaceCollector(templates_path, device, registry)
    VppctlShowMemoryVerboseCollector(templates_path, device, registry)
    VppctlShowIPFibMemHeapCollector(templates_path, device, registry)
