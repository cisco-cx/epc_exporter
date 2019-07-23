package parser_test

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"

	"github.com/neermitt/epc_exporter/parser"
)

var testData = []struct {
	Name     string
	Input    string
	Template string
}{
	{"show npu utilization table", "show_npu_utilization_table.txt", "show_npu_utilization_table.template"},
	{"show port datalink counters", "show_port_datalink_counters.txt", "show_port_datalink_counters.template"},
	{"show port utilization table", "show_port_utilization_table.txt", "show_port_utilization_table.template"},
}

func TestParse(t *testing.T) {

	for _, td := range testData {
		t.Run(td.Name, func(t *testing.T) {

			record := make(chan []interface{})

			err := parser.Parse("../templates/"+td.Template, "../test/data/"+td.Input, record)
			assert.NoError(t, err)

			// print to console
			for {
				// get next row
				row, ok := <-record
				if !ok {
					break
				}

				fmt.Printf("%+q\n", row)
			}
		})
	}

}
