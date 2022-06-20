ARG KEYSTONE_IMAGE_TAG=current-tripleo
FROM tripleomaster/centos-binary-keystone:${KEYSTONE_IMAGE_TAG}

COPY keystone-wsgi-main.conf /etc/httpd/conf.d/keystone-wsgi-main.conf
COPY runtime /runtime

CMD ["/bin/sh", "/runtime/startup.sh"]
