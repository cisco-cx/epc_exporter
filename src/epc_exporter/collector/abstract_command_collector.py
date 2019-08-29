"""
Abstract collector module
"""

import textfsm
from prometheus_client import CollectorRegistry

from device import AbstractDevice


class AbstractCommandCollector(object):
    """ Base class for Command Collector """

    def __init__(self, template_file: str, device: AbstractDevice, registry:
                 CollectorRegistry):
        with open(template_file, "r") as template:
            self._parser = textfsm.TextFSM(template)

        self._device = device

        if registry:
            registry.register(self)
