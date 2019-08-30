current_dir = $(shell pwd)

.PHONY: deps
deps:  ## install python dependencies
	pip3 install -r requirements.txt

.PHONY: fmt
fmt: yapf lint ## format code

.PHONY: yapf
yapf:
	docker run --rm -v $$(pwd):/tmp --entrypoint sh tobegit3hub/yapf-docker \
		-c "yapf -i \$$(find /tmp/src/epc_exporter -type f -name '*.py')"

.PHONY: lint
lint: pylint flake8 ## lint code

.PHONY: pylint
pylint:
	docker run --rm -v $$(pwd)/src/epc_exporter:/code/epc_exporter \
	    -v $$(pwd)/.pylintrc:/code/.pylintrc -w /code \
	    -e "PYTHONPATH=/code/epc_exporter" clburlison/pylint \
		pylint --disable=import-error,too-few-public-methods \
		--ignore-patterns=.*_test.* epc_exporter

.PHONY: flake8
flake8:
	docker run --rm -v $$(pwd)/src:/code --entrypoint sh alpine/flake8:3.5.0 \
		-c "flake8  \$$(find /code/epc_exporter -type f -name '*.py')"

.PHONY: dep-freeze
dep-freeze: ## freeze requirements.txt
	pip freeze --local > requirements.txt

# Runs tests in short mode, without database adapters
.PHONY: test
test: ## test python code
	export PYTHONPATH=$(current_dir)/src/epc_exporter/ && python3 -m unittest collector.collectors_test_suite

.PHONY: docker-build
docker-build: ## build docker image with local tag
	docker build -t docker.io/ciscocx/epc_exporter:local .

help: ## Print the list of Makefile targets
	@# Taken from https://github.com/spf13/hugo/blob/master/Makefile
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
    cut -d ":" -f1- | \
    awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
