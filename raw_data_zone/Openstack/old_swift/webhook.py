from swift.common.http import is_success
from swift.common.swob import wsgify
from swift.common.utils import split_path, get_logger
from swift.common.request_helpers import get_sys_meta_prefix
from swift.proxy.controllers.base import get_container_info
from eventlet import Timeout
import six
if six.PY3:
    from eventlet.green.urllib import request as urllib2
else:
    from eventlet.green import urllib2
URL = "http://141.115.103.32:8080"
ENDPOINT_PATH = "/api/experimental"
DAG_TO_TRIGGER = "new_input"
# x-container-sysmeta-webhook
SYSMETA_WEBHOOK = get_sys_meta_prefix('container') + 'webhook'


class WebhookMiddleware(object):
    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='webhook')

    @wsgify
    def __call__(self, req):
        obj = None
        try:
            (version, account, container, obj) = \
                split_path(req.path_info, 4, 4, True)
        except ValueError:
            # not an object request
            pass
        if obj and req.method == 'PUT':
            # create a POST request with obj name as body
            payload = {
                "conf": {"swift_id": obj, "swift_container": container,
                         "swift_user": account, "swift_version": version}}
            webhook_req = urllib2.Request(URL + ENDPOINT_PATH + "/dags/"+DAG_TO_TRIGGER+"/dag_runs", data= payload )
            with Timeout(20):
                try:
                    urllib2.urlopen(webhook_req).read()
                except (Exception, Timeout):
                    self.logger.exception(
                        'failed POST to webhook %s' % webhook)
                else:
                    self.logger.info(
                        'successfully called webhook %s' % webhook)
        return self.app



def webhook_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def webhook_filter(app):
        return WebhookMiddleware(app, conf)
    return webhook_filter