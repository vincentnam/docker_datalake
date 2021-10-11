ARG SWIFT_VERSION
FROM openstackswift/saio:$SWIFT_VERSION
# Overwrite conf

ARG AIRFLOW_HOST
RUN mkdir -p /mnt/sdb1/1 /mnt/sdb1/2 && \
    chown swift:swift /mnt/sdb1/* &&\
    for x in {1..2}; do ln -s /mnt/sdb1/$x /srv/$x; done && \
    mkdir -p /srv/1/node/sdb1 /srv/1/node/sdb5 \
              /srv/2/node/sdb2 /srv/2/node/sdb6 && \
    mkdir -p /var/run/swift && \
    mkdir -p /var/cache/swift /var/cache/swift2 && \
    chown -R swift:swift /var/run/swift && \
    chown -R swift:swift /var/cache/swift* && \
    #for x in {1..2}; do chown -R ${USER}:${USER} /srv/$x/; done
    chown -R swift:swift /srv/1 && \
    chown -R swift:swift /srv/2

COPY ./swift/ /etc/swift/
COPY ./new_data_trigger.py /usr/local/src/swift/swift/common/middleware/new_data_trigger.py
COPY ./config.py /usr/local/src/swift/swift/common/middleware/config.py
#RUN sed -i "s/URL = \"\"/URL = \"http:\/\/$AIRFLOW_HOST:8081\"/g" /usr/local/src/swift/swift/common/middleware/new_data_trigger.py
#TODO : Add port custom for Airflow webserver (here : 8081)
COPY ./bin/ /swift/bin/
COPY ./conf/rsyncd.conf /etc/
COPY ./conf/10-swift.conf /etc/rsyslog.d/10-swift.conf
COPY ./conf/supervisord.conf /etc/supervisord.conf

# TODO: Add /srv/ folder for each server defined
