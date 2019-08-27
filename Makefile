current_dir = $(shell pwd)

.PHONY: deps
deps:  ## install python dependencies
	pip3 install -r requirements.txt

.PHONY: fmt
fmt: ## format code
	docker run --rm -v $$(pwd):/tmp --entrypoint sh tobegit3hub/yapf-docker -c "yapf -i \$$(find /tmp/src/epc_exporter -type f -name '*.py')"
	docker run --rm -v $$(pwd):/tmp --entrypoint sh alpine/flake8:3.5.0 -c "flake8 --ignore=E501 \$$(find /tmp/src/epc_exporter -type f -name '*.py')"

.PHONY: dep-freeze
dep-freeze: ## freeze requirements.txt
	pip freeze --local > requirements.txt

# Runs tests in short mode, without database adapters
.PHONY: test
test: ## test python code
	export PYTHONPATH=$(current_dir)/src/epc_exporter/ && python -m unittest collector.collectors_test_suite

.PHONY: docker
docker: ## build docker image with local tag
	docker build -t docker.io/ciscocx/epc_exporter:local .

help: ## Print the list of Makefile targets
	@# Taken from https://github.com/spf13/hugo/blob/master/Makefile
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
    cut -d ":" -f1- | \
    awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
