FROM debian:bookworm-slim

ARG SWIFT_VERSION=2.34.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir "swift==${SWIFT_VERSION}"

RUN mkdir -p /opt/swift-scripts /etc/swift && chown -R root:root /opt/swift-scripts

COPY entrypoints/build-rings.sh /opt/swift-scripts/build-rings.sh
RUN chmod +x /opt/swift-scripts/build-rings.sh

WORKDIR /opt/swift-scripts
ENTRYPOINT ["/opt/swift-scripts/build-rings.sh"]