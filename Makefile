
.PHONY: deps
deps:
		pip3 install -r requirements.txt

.PHONY: docker
docker:
		docker build -t docker.io/ciscocx/epc_exporter:local .