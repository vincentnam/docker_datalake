FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        attr \
        liberasurecode1 \
        memcached \
        python-dnspython \
        python-eventlet \
        python-greenlet \
        python-lxml \
        python-netifaces \
        python-pastedeploy \
        python-pip \
        python-pyeclib \
        python-setuptools \
        python-simplejson \
        python-xattr \
        rsyslog \
        rsync \
        sqlite3 \
        software-properties-common \
        sudo \
        xfsprogs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade "pip < 21.0"


RUN pip install --upgrade pip setuptools==44.1.1 pytz setuptools-rust==0.9.0 cryptography==3.3.2 requests==2.27.1

RUN apt-get update && \
    apt-get install -y --no-install-recommends git-core && \
    git clone --branch 3.8.1 --single-branch --depth 1 https://github.com/openstack/python-swiftclient.git /usr/local/src/python-swiftclient && \
    cd /usr/local/src/python-swiftclient && python setup.py develop

RUN git clone --branch 2.24.0 --single-branch --depth 1 https://github.com/openstack/swift.git /usr/local/src/swift && \
    cd /usr/local/src/swift && python setup.py develop && \
    apt-get remove -y --purge git-core git && \
    apt-get autoremove -y --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY swift /etc/swift/
COPY conf/rsyncd.conf /etc/
COPY bin /swift/bin
COPY conf/bashrc /swift/.bashrc
COPY conf/supervisord.conf /etc/supervisord.conf
COPY conf/10-swift.conf /etc/rsyslog.d/10-swift.conf
RUN     easy_install supervisor; mkdir /var/log/supervisor/ && \
    # create swift user and group
    mkdir -p /var/cache/swift /var/cache/swift2 && \
    /usr/sbin/useradd -m -d /swift -U swift && \
    sed -i 's/RSYNC_ENABLE=false/RSYNC_ENABLE=true/' /etc/default/rsync && \
    sed -i 's/SLEEP_BETWEEN_AUDITS = 30/SLEEP_BETWEEN_AUDITS = 86400/' /usr/local/src/swift/swift/obj/auditor.py && \
    chmod +x /swift/bin/* && \
    cp /usr/local/src/swift/test/sample.conf /etc/swift/test.conf && \
    sed -i 's/\$PrivDropToGroup syslog/\$PrivDropToGroup adm/' /etc/rsyslog.conf && \
    sed -i 's/\module(load="imklog" permitnonkernelfacility="on")/\#module(load="imklog" permitnon-kernelfacility="on")/' /etc/rsyslog.conf && \
    mkdir -p /var/log/swift/hourly; chown -R syslog.adm /var/log/swift; chmod -R g+w /var/log/swift && \
    echo swift:fingertips | chpasswd; usermod -a -G sudo swift && \
    echo %sudo ALL=NOPASSWD: ALL >> /etc/sudoers


CMD ["/bin/bash", "/swift/bin/start.sh"]
