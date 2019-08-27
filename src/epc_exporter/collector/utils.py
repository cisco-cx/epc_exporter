from prometheus_client.utils import floatToGoString

units = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}


def parse_size(size):
    if size == '--':
        return 0
    number = size[:-1]
    unit = size[-1]
    return int(float(number) * units[unit])


def add_gauge_metrics(metric, labels, value):
    if value != "n/a":
        metric.add_metric(labels=labels, value=value)


def add_histogram_metrics(metric, labels, upper_bounds, values, sum_value):
    if values[0] != "n/a":
        buckets = []
        acc = 0
        for index, bound in enumerate(upper_bounds):
            acc += float(values[index])
            buckets.append([floatToGoString(bound), acc])

        metric.add_metric(labels=labels, buckets=buckets, sum_value=sum_value)
