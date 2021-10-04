from swift.common.swob import wsgify
from swift.common.utils import split_path, get_logger

from swift.common.request_helpers import get_sys_meta_prefix
from swift.proxy.controllers.base import get_container_info
from eventlet import Timeout
from swift.common.utils import register_swift_info

URL = ""
ENDPOINT_PATH = "/api/experimental"
DAG_NAME = "test"
#
# import ConfigParser
# config = ConfigParser.ConfigParser().read(CONFIG_PATH).sections()

import six

if six.PY3:
    from eventlet.green.urllib import request as urllib2
else:
    from eventlet.green import urllib2
import requests
from swift.common.http import is_success
from config import AIRFLOW_API_URL


class NewDataTriggerMiddleware(object):
    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='new_data_trigger')
        self.airflow_api_url = AIRFLOW_API_URL
        self.airflow_new_upload_dag_id = "data-processing-upload"

    @wsgify
    def __call__(self, req):
        resp = req.get_response(self.app)
        if req.method == 'PUT':
            obj = None
            airflow_post_body = {}
            try:
                version, account, container, obj = split_path(req.path_info, 4, 4, True)
                airflow_post_body = {"conf": {"swift_version": version,
                                              "swift_user": account,
                                              "swift_container": container,
                                              "swift_obj_id": obj
                                              }
                                     }
                self.logger.info('Airflow post request body: %s' % airflow_post_body)
            except ValueError:
                # not an object request
                pass

            if obj and is_success(resp.status_int):
                # ignore mqtt flux
                if req.headers.get("x-object-meta-source") == "mqtt":
                    return resp
                try:
                    requests.post(
                        url=self.airflow_api_url + '/dags/' + self.airflow_new_upload_dag_id + '/dagRuns',
                        json=airflow_post_body,
                        auth=('airflow', 'airflow')
                    )
                except Exception as e:
                    self.logger.exception('Failed POST to Airflow: %s' % e)

        return resp


def new_data_trigger_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def new_data_trigger_filter(app):
        return NewDataTriggerMiddleware(app, conf)

    return new_data_trigger_filter
