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
        sudo \
        xfsprogs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip setuptools pytz setuptools-rust==0.9.0 cryptography==3.3.2

RUN apt-get update && \
    apt-get install -y --no-install-recommends git-core && \
    git clone --branch 3.8.1 --single-branch --depth 1 https://github.com/openstack/python-swiftclient.git /usr/local/src/python-swiftclient && \
    cd /usr/local/src/python-swiftclient && python setup.py develop && \
    git clone --branch 2.24.0 --single-branch --depth 1 https://github.com/openstack/swift.git /usr/local/src/swift && \
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
RUN	easy_install supervisor; mkdir /var/log/supervisor/ && \
    # create swift user and group
    mkdir -p /var/cache/swift /var/cache/swift2 && \
    /usr/sbin/useradd -m -d /swift -U swift && \
    sed -i 's/RSYNC_ENABLE=false/RSYNC_ENABLE=true/' /etc/default/rsync && \
    sed -i 's/SLEEP_BETWEEN_AUDITS = 30/SLEEP_BETWEEN_AUDITS = 86400/' /usr/local/src/swift/swift/obj/auditor.py && \
    chmod +x /swift/bin/* && \
    cp /usr/local/src/swift/test/sample.conf /etc/swift/test.conf && \
    sed -i 's/\$PrivDropToGroup syslog/\$PrivDropToGroup adm/' /etc/rsyslog.conf && \
    sed -i 's/\module(load="imklog" permitnonkernelfacility="on")/\#module(load="imklog" permitnonkernelfacility="on")/' /etc/rsyslog.conf && \
    mkdir -p /var/log/swift/hourly; chown -R syslog.adm /var/log/swift; chmod -R g+w /var/log/swift && \
    echo swift:fingertips | chpasswd; usermod -a -G sudo swift && \
    echo %sudo ALL=NOPASSWD: ALL >> /etc/sudoers


CMD ["/bin/bash", "/swift/bin/start.sh"]

#FROM python:3.4
#
#RUN apt-get update && apt-get -y install curl gcc memcached rsync sqlite3 xfsprogs \
#                     git-core libffi-dev python-setuptools \
#                     liberasurecode-dev libssl-dev && \
#                    apt-get install -y python-coverage python-dev python-nose \
#                     python-xattr python-eventlet \
#                     python-greenlet python-pastedeploy \
#                     python-netifaces python-pip python-dnspython \
#                     python-mock
#
#RUN cd $HOME && git clone https://github.com/openstack/python-swiftclient.git && cd $HOME/python-swiftclient && python setup.py develop
#RUN cd $HOME && git clone https://github.com/openstack/swift.git && cd swift &&  pip install --no-binary cryptography -r requirements.txt && python setup.py develop
#RUN cd $HOME/swift/ &&  pip install -r test-requirements.txt
#RUN mkdir /etc/swift /var/swift /var/log/swift  /var/cache/swift /var/cache/swift2
#RUN service memcached start && service rsync start
#
#RUN sed -i 's/RSYNC_ENABLE=false/RSYNC_ENABLE=true/g' /etc/default/rsync
#RUN cp $HOME/swift/doc/saio/rsyslog.d/10-swift.conf /etc/rsyslog.d && mkdir -p /var/log/swift/hourly && chmod -R g+w /var/log/swift/ \
#    && apt-get -y install rsyslog && sed -i 's/model(load="imklog")/#model(load="imklog")/g' /etc/rsyslog.conf
#
#RUN cp -r $HOME/swift/doc/saio/bin/ $HOME/bin/ && rm $HOME/bin/remakerings && \
#echo '#!/bin/bash \n\
#set -e \n\
#cd /etc/swift \n\
#rm -f *.builder *.ring.gz backups/*.builder backups/*.ring.gz \n\
## Create part_power (?) replicas min_part_hour \n\
#swift-ring-builder object.builder create 10 1 1 \n\
#swift-ring-builder object.builder add r1z1-127.0.0.1:6210/sdb1 1 \n\
#swift-ring-builder object.builder add r1z2-127.0.0.2:6220/sdb2 1 \n\
##swift-ring-builder object.builder add r1z3-127.0.0.3:6230/sdb3 1 \n\
##swift-ring-builder object.builder add r1z4-127.0.0.4:6240/sdb4 1 \n\
#swift-ring-builder object.builder rebalance \n\
#swift-ring-builder object-1.builder create 10 1 1 \n\
#swift-ring-builder object-1.builder add r1z1-127.0.0.1:6210/sdb1 1 \n\
#swift-ring-builder object-1.builder add r1z2-127.0.0.2:6220/sdb2 1 \n\
##swift-ring-builder object-1.builder add r1z3-127.0.0.3:6230/sdb3 1 \n\
##swift-ring-builder object-1.builder add r1z4-127.0.0.4:6240/sdb4 1 \n\
#swift-ring-builder object-1.builder rebalance \n\
#swift-ring-builder object-2.builder create 10 1 1 \n\
#swift-ring-builder object-2.builder add r1z1-127.0.0.1:6210/sdb1 1 \n\
#swift-ring-builder object-2.builder add r1z1-127.0.0.1:6210/sdb5 1 \n\
#swift-ring-builder object-2.builder add r1z2-127.0.0.2:6220/sdb2 1 \n\
#swift-ring-builder object-2.builder add r1z2-127.0.0.2:6220/sdb6 1 \n\
##swift-ring-builder object-2.builder add r1z3-127.0.0.3:6230/sdb3 1 \n\
##swift-ring-builder object-2.builder add r1z3-127.0.0.3:6230/sdb7 1 \n\
##swift-ring-builder object-2.builder add r1z4-127.0.0.4:6240/sdb4 1 \n\
##swift-ring-builder object-2.builder add r1z4-127.0.0.4:6240/sdb8 1 \n\
#swift-ring-builder object-2.builder rebalance \n\
#swift-ring-builder container.builder create 10 1 1 \n\
#swift-ring-builder container.builder add r1z1-127.0.0.1:6211/sdb1 1 \n\
#swift-ring-builder container.builder add r1z2-127.0.0.2:6221/sdb2 1 \n\
##swift-ring-builder container.builder add r1z3-127.0.0.3:6231/sdb3 1 \n\
##swift-ring-builder container.builder add r1z4-127.0.0.4:6241/sdb4 1 \n\
#swift-ring-builder container.builder rebalance \n\
#swift-ring-builder account.builder create 10 1 1 \n\
#swift-ring-builder account.builder add r1z1-127.0.0.1:6212/sdb1 1 \n\
#swift-ring-builder account.builder add r1z2-127.0.0.2:6222/sdb2 1 \n\
##swift-ring-builder account.builder add r1z3-127.0.0.3:6232/sdb3 1 \n\
##swift-ring-builder account.builder add r1z4-127.0.0.4:6242/sdb4 1 \n\
#swift-ring-builder account.builder rebalance \n\
#' > $HOME/bin/remakerings && chmod +x $HOME/bin/* && cp $HOME/swift/test/sample.conf /etc/swift/test.conf
#COPY start.sh /usr/bin/start.sh
#COPY conf/rsyncd.conf /etc/rsyncd.conf
#COPY swift/ /etc/swift/
#RUN mkdir -p /srv/1/node/sdb1 /srv/1/node/sdb5 /srv/2/node/sdb2 /srv/2/node/sdb6 /var/run/swift
#
#CMD start.sh