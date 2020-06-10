from swift.common.http import is_success
from swift.common.swob import wsgify
from swift.common.utils import split_path, get_logger
from swift.common.request_helpers import get_sys_meta_prefix
from swift.proxy.controllers.base import get_container_info
from eventlet import Timeout
from swift.common.utils import register_swift_info

URL = "airflow:8080"
ENDPOINT_PATH="/api/experimental"

#
# import ConfigParser
# config = ConfigParser.ConfigParser().read(CONFIG_PATH).sections()
import six
if six.PY3:
    from eventlet.green.urllib import request as urllib2
else:
    from eventlet.green import urllib2
import requests
# x-container-sysmeta-webhook
SYSMETA_WEBHOOK = get_sys_meta_prefix('container') + 'webhook'


class NewDataTriggerMiddleware(object):
    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='newdatatrigger')

    @wsgify
    def __call__(self, req):
        # print(req)
        # print(req.headers)
        # print(req.environ)
        # self.logger.info(req)
        obj = None
        try:
            (version, account, container, obj) = \
                split_path(req.path_info, 4, 4, True)
            print("COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU COUCOU ")

            rep = requests.post(URL + ENDPOINT_PATH + "/dags/new_input/dag_runs", )

        except ValueError:
            # not an object request
            pass

        # No response return = bug
        resp = req.get_response(self.app)

        return resp


def new_data_trigger_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def new_data_trigger_filter(app):
        return NewDataTriggerMiddleware(app, conf)
    return new_data_trigger_filter
