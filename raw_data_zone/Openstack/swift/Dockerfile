ARG SWIFT_VERSION
FROM dockerswiftaio/docker-swift:$SWIFT_VERSION
# Overwrite conf
COPY ./swift/ /etc/swift/
COPY ./new_data_trigger.py /usr/local/src/swift/swift/common/middleware/new_data_trigger.py
COPY ./bin/ /swift/bin/
COPY ./conf/rsyncd.conf /etc/
COPY ./conf/10-swift.conf /etc/rsyslog.d/10-swift.conf
COPY ./conf/supervisord.conf /etc/supervisord.conf