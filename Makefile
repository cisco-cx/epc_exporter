current_dir = $(shell pwd)

.PHONY: deps
deps:
	pip3 install -r requirements.txt

.PHONY: dep-freeze
dep-freeze:
	pip freeze --local > requirements.txt

# Runs tests in short mode, without database adapters
.PHONY: test
test:
	export PYTHONPATH=$(current_dir)/src/epc_exporter/ && python -m unittest collector.collectors_test_suite

.PHONY: docker
docker:
	docker build -t docker.io/ciscocx/epc_exporter:local .
