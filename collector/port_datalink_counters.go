package collector

import (
	"fmt"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/common/log"

	"github.com/neermitt/epc_exporter/parser"
)

const (
	portDataLinkCollectorSubsystem = "port_datalink"
)

type portDatLinkCounterCollector struct {
	unicastFrames   []typedDesc
	multicastFrames []typedDesc
	broadcastFrames []typedDesc
}

func init() {
	registerCollector(portDataLinkCollectorSubsystem, defaultEnabled, NePortDatLinkCounter)
}

// NePortDatLinkCounter returns a new Collector exposing NPU stats.
func NePortDatLinkCounter() (Collector, error) {
	return &portDatLinkCounterCollector{
		unicastFrames: []typedDesc{
			{prometheus.NewDesc(prometheus.BuildFQName(namespace, npuCollectorSubsystem, "unicastFrames_rx"), "Unicast Frames Rx counter.", []string{"port"}, nil), prometheus.CounterValue},
			{prometheus.NewDesc(prometheus.BuildFQName(namespace, npuCollectorSubsystem, "unicastFrames_tx"), "Unicast Frames Tx counter.", []string{"port"}, nil), prometheus.CounterValue},
		},
		multicastFrames: []typedDesc{
			{prometheus.NewDesc(prometheus.BuildFQName(namespace, npuCollectorSubsystem, "multicastFrames_rx"), "Multicast Frames Rx counter.", []string{"port"}, nil), prometheus.CounterValue},
			{prometheus.NewDesc(prometheus.BuildFQName(namespace, npuCollectorSubsystem, "multicastFrames_tx"), "Multicast Frames Tx counter.", []string{"port"}, nil), prometheus.CounterValue},
		},
		broadcastFrames: []typedDesc{
			{prometheus.NewDesc(prometheus.BuildFQName(namespace, npuCollectorSubsystem, "broadcastFrames_rx"), "Broadcast Frames Rx counter.", []string{"port"}, nil), prometheus.CounterValue},
			{prometheus.NewDesc(prometheus.BuildFQName(namespace, npuCollectorSubsystem, "broadcastFrames_tx"), "Broadcast Frames Tx counter.", []string{"port"}, nil), prometheus.CounterValue},
		},
	}, nil
}

func (c *portDatLinkCounterCollector) Update(ch chan<- prometheus.Metric) error {
	record := make(chan []interface{})
	err := parser.Parse("templates/show_port_datalink_counters.template", "test/data/show_port_datalink_counters.txt", record)
	if err != nil {
		return fmt.Errorf("couldn't get port datalink counters: %s", err)
	}

	for {
		// get next row
		row, ok := <-record
		if !ok {
			break
		}
		log.Debugf("return npu usage %+q", row)
		port := row[0].(string)

		metric := row[1].(string)
		switch metric {
		case "Unicast frames":
			ch <- c.unicastFrames[0].mustNewConstMetric(stringToFloat(row[2].(string)), port)
			ch <- c.unicastFrames[1].mustNewConstMetric(stringToFloat(row[4].(string)), port)
		case "Multicast frames":
			ch <- c.multicastFrames[0].mustNewConstMetric(stringToFloat(row[2].(string)), port)
			ch <- c.multicastFrames[1].mustNewConstMetric(stringToFloat(row[4].(string)), port)
		case "Broadcast frames":
			ch <- c.broadcastFrames[0].mustNewConstMetric(stringToFloat(row[2].(string)), port)
			ch <- c.broadcastFrames[1].mustNewConstMetric(stringToFloat(row[4].(string)), port)
		}

	}
	return nil
}
