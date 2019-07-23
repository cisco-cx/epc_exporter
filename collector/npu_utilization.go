package collector

import (
	"fmt"
	"strconv"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/common/log"

	"github.com/neermitt/epc_exporter/parser"
)

const (
	npuCollectorSubsystem = "npu"
)

type statCollector struct {
	metric []typedDesc
}

func init() {
	registerCollector("npu", defaultEnabled, NewNPUCollector)
}

// NewNPUCollector returns a new Collector exposing NPU stats.
func NewNPUCollector() (Collector, error) {
	return &statCollector{
		metric: []typedDesc{
			{prometheus.NewDesc(prometheus.BuildFQName(namespace, npuCollectorSubsystem, "usage1"), "1m usage percent.", []string{"npu"}, nil), prometheus.GaugeValue},
			{prometheus.NewDesc(prometheus.BuildFQName(namespace, npuCollectorSubsystem, "usage5"), "5m usage percent.", []string{"npu"}, nil), prometheus.GaugeValue},
			{prometheus.NewDesc(prometheus.BuildFQName(namespace, npuCollectorSubsystem, "usage15"), "15m usage percent.", []string{"npu"}, nil), prometheus.GaugeValue},
		},
	}, nil
}

func (c *statCollector) Update(ch chan<- prometheus.Metric) error {
	record := make(chan []interface{})
	err := parser.Parse("templates/show_npu_utilization_table.template", "test/data/show_npu_utilization_table.txt", record)
	if err != nil {
		return fmt.Errorf("couldn't get npu usage: %s", err)
	}

	for {
		// get next row
		row, ok := <-record
		if !ok {
			break
		}
		log.Debugf("return npu usage %+q", row)
		npuId := row[0].(string)

		ch <- c.metric[0].mustNewConstMetric(stringToFloat(row[1].(string)), npuId)
		ch <- c.metric[1].mustNewConstMetric(stringToFloat(row[2].(string)), npuId)
		ch <- c.metric[2].mustNewConstMetric(stringToFloat(row[3].(string)), npuId)
	}
	return nil
}

func stringToFloat(val string) float64 {
	if s, err := strconv.ParseFloat(val, 64); err == nil {
		return s
	}

	return 0.0
}
