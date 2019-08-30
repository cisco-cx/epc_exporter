"""
Utility methods to be used in parsing and Prometheus metrics conversion
"""
from prometheus_client.utils import floatToGoString

_UNITS = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}


def parse_size(size):
    """Parses memory size"""
    if size == '--':
        return 0
    number = size[:-1]
    unit = size[-1]
    return int(float(number) * _UNITS[unit])


def add_gauge_metrics(metric, labels, value):
    """Add a sample of values to gauge metrics with labels"""
    if value != "n/a":
        metric.add_metric(labels=labels, value=value)


def add_histogram_metrics(metric, labels, upper_bounds, values, sum_value):
    """Add a sample of values to histogram metrics with labels"""
    if values[0] != "n/a":
        buckets = []
        acc = 0
        # convert the point values to cumulative values for adding to histogram
        for index, bound in enumerate(upper_bounds):
            acc += float(values[index])
            buckets.append([floatToGoString(bound), acc])

        metric.add_metric(labels=labels, buckets=buckets, sum_value=sum_value)
