import sys

from prometheus_client import REGISTRY, write_to_textfile

from src.epc_exporter.collector import TestCollector, NPUUtilizationCollector, PortUtilizationCollector

if __name__ == "__main__":
    "Running in text collector mode"
    output_path = sys.argv[1]

    TestCollector()
    NPUUtilizationCollector()
    PortUtilizationCollector()
    write_to_textfile(output_path, REGISTRY)
