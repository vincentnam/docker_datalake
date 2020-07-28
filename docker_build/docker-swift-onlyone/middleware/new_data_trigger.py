Skip
to
content
Search or jump
to…

Pulls
Issues
Marketplace
Explore


@vincentnam


vincentnam
/
docker_datalake
1
0
0
Code
Issues
Pull
requests
Actions
Projects
Wiki
Security
Insights
More
docker_datalake / docker_build / docker - swift - onlyone / middleware / new_data_trigger.py /


@vincentnam


vincentnam
Testing
the
architecture
Latest
commit
7
c0de7e
8
days
ago
History
1
contributor
67
lines(57
sloc)  2.05
KB

Code
navigation is available!
Navigate
your
code
with ease.Click on function and method calls to jump to their definitions or references in the same repository.Learn more

from swift.common.http import is_success
from swift.common.swob import wsgify
from swift.common.utils import split_path, get_logger
from swift.common.request_helpers import get_sys_meta_prefix
from swift.proxy.controllers.base import get_container_info
from eventlet import Timeout
from swift.common.utils import register_swift_info

URL = "http://141.115.103.32:8080"
ENDPOINT_PATH = "/api/experimental"
DAG_TO_TRIGGER = "new_input"
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
import json


class NewDataTriggerMiddleware(object):
    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='newdatatrigger')

    @wsgify
    def __call__(self, req):
        print(req)
        print(req.headers)
        print(req.path_info)
        # print(req.environ)
        # self.logger.info(req)
        obj = None
        try:
            (version, account, container, obj) = \
                split_path(req.path_info, 4, 4, True)


        except ValueError:
            # not an object request
            resp = req.get_response(self.app)

            return resp
        if req.method == 'PUT':
            print(obj)
            payload = {"conf": {"swift_id": obj, "swift_container": container,
                                "swift_user": account, "swift_version": version}}
            rep = requests.post(
                URL + ENDPOINT_PATH + "/dags/" + DAG_TO_TRIGGER + "/dag_runs",
                data=json.dumps(payload))
            print(rep.text)
        self.logger.info(rep.headers)
        self.logger.info(rep.text)
        # No response return = bug
        resp = req.get_response(self.app)

        return resp


def new_data_trigger_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def new_data_trigger_filter(app):
        return NewDataTriggerMiddleware(app, conf)

    return new_data_trigger_filter
