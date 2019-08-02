from prometheus_client import REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily


class TestCollector(object):
    """Collector for python platform information"""

    def __init__(self, registry=REGISTRY):
        info = self._info()
        self._metrics = [
            self._add_metric("test", "test metrics", info)
        ]
        if registry:
            registry.register(self)

    def collect(self):
        return self._metrics

    @staticmethod
    def _add_metric(name, documentation, value):
        g = GaugeMetricFamily(name, documentation)
        g.add_metric(labels={}, value=value)
        return g

    def _info(self):
        return 1
