ARG BASEVERSION=latest
FROM docker.io/ciscocx/batch_exporter:${BASEVERSION}

RUN apt-get update \
    && apt-get -y install python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /epc_exporter/
RUN cd /epc_exporter && pip3 install -r requirements.txt
COPY ./src/epc_exporter /epc_exporter
COPY ./templates /epc_exporter/templates
COPY ./test/data /epc_exporter/data
COPY ./supervisor.d/epc_exporter.conf ./supervisor.d/