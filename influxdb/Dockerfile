FROM alpine
RUN apk add curl bash
RUN curl -o influxdb_client_2.0.0-beta.16_linux_amd64.tar.gz https://dl.influxdata.com/influxdb/releases/influxdb_client_2.0.0-beta.16_linux_amd64.tar.gz
RUN tar xvfz influxdb_client_2.0.0-beta.16_linux_amd64.tar.gz && cp influxdb_client_2.0.0-beta.16_linux_amd64/influx /usr/local/bin/



