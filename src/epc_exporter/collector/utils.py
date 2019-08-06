from prometheus_client.utils import floatToGoString


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
