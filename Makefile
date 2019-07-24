
.PHONY: deps
deps:
		go mod download


.PHONY: fmt
fmt:
		go fmt  ./...


# Runs tests in short mode, without database adapters
.PHONY: quicktest
quicktest:
		go test -failfast -short ./...

# Runs tests in short mode, without database adapters
.PHONY: test
test:
		go test ./...

.PHONY: build
build: deps
		CGO_ENABLED=0 GOOS=$(os) go build -o epc_exporter
