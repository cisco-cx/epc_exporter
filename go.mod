module github.com/neermitt/epc_exporter

go 1.12

require (
	github.com/TobiEiss/go-textfsm v0.0.0-20190710064052-032be7312a18
	github.com/prometheus/client_golang v1.0.0
	github.com/prometheus/common v0.4.1
	github.com/sirupsen/logrus v1.4.2 // indirect
	github.com/stretchr/testify v1.3.0
	gopkg.in/alecthomas/kingpin.v2 v2.2.6
)

replace github.com/TobiEiss/go-textfsm v0.0.0-20190710064052-032be7312a18 => github.com/neermitt/go-textfsm v0.0.0-20190723175344-620873a131c4
