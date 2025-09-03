FROM debian:bookworm-slim

ARG SWIFT_VERSION=2.34.0
ENV DEBIAN_FRONTEND=noninteractive

# create swift user
RUN groupadd --system swift && useradd --system --create-home --home-dir /home/swift -g swift swift

# runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv rsync openssl curl ca-certificates \
    libpython3-dev build-essential \
  && rm -rf /var/lib/apt/lists/*

# install swift packages (proxy server and tempauth)
RUN pip3 install --no-cache-dir "python-swiftclient==${SWIFT_VERSION}" "swift==${SWIFT_VERSION}"

# create dirs
RUN mkdir -p /etc/swift /var/log/swift /var/cache/swift /srv/node /opt/swift-scripts \
  && chown -R swift:swift /etc/swift /var/log/swift /var/cache/swift /srv/node /opt/swift-scripts

COPY entrypoints/start-proxy.sh /opt/swift-scripts/start-proxy.sh
RUN chmod +x /opt/swift-scripts/start-proxy.sh && chown swift:swift /opt/swift-scripts/start-proxy.sh

USER swift
WORKDIR /home/swift

EXPOSE 8080
VOLUME ["/etc/swift", "/srv/node", "/var/log/swift"]

CMD ["/opt/swift-scripts/start-proxy.sh"]