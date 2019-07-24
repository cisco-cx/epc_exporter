# build stage
FROM golang:1.12.5-stretch AS build-env
ADD . /src
WORKDIR /src
RUN make build

# final stage
FROM alpine
WORKDIR /app
COPY --from=build-env /src/epc_exporter /app/
ENTRYPOINT ["./epc_exporter"]
EXPOSE 9110

