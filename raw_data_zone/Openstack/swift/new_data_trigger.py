from swift.common.swob import wsgify
from swift.common.utils import split_path, get_logger
import six

if six.PY3:
    from eventlet.green.urllib import request as urllib2
else:
    from eventlet.green import urllib2
import requests

class NewUploadTriggerMiddleware(object):
    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='new_upload_trigger')
        self.airflow_api_url = "http://<to_complete>:8080/api/v1"
        self.airflow_new_upload_dag_id = "test"

    @wsgify
    def __call__(self, req):
        if req.headers.get("x-object-meta-source") == "mqtt":
            return req.get_response(self.app)
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
            print("ValueError: %s" % ValueError)
            # not an object request
            pass

        if req.method == 'PUT':
            try:
                resp = requests.post(
                    url=self.airflow_api_url + '/dags/' + self.airflow_new_upload_dag_id + '/dagRuns',
                    json=airflow_post_body,
                    auth=('airflow', 'airflow')
                )
            except Exception as e:
                self.logger.exception('Failed POST to Airflow: %s' % e)
            else:
                self.logger.info(
                    'Successfully triggered Airflow %s' % resp.text)
                    
        return req.get_response(self.app)


def new_data_trigger_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def new_upload_trigger_filter(app):
        return NewUploadTriggerMiddleware(app, conf)

    return new_upload_trigger_filter
