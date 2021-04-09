import requests
from swift.common.swob import wsgify
from swift.common.utils import split_path, get_logger


class TestNewUploadTriggerMiddleware(object):
    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='test_new_upload_trigger')
        self.airfloa_api_url = "http://127.0.0.1:8080/api/v1"
        self.airflow_test_new_upload_dag_id = "test_new_upload"

    @wsgify
    def __call__(self, req):
        try:
            version, account, container, obj = split_path(req.path_info, 4, 4, True)

            airflow_post_body = {"conf": {"swift_version": version,
                                          "swift_user": account,
                                          "swift_container": container,
                                          "swift_obj_id": obj
                                          }
                                 }
            self.logger.info('airflow_post_body: %s' % airflow_post_body)
        except ValueError:
            print("ValueError: %s" % ValueError)
            # not an object request
            pass
        try:
            resp = requests.post(
                url=self.airfloa_api_url + '/dags/' + self.airflow_test_new_upload_dag_id + '/dagRuns',
                json=airflow_post_body,
                auth=('airflow', 'airflow')
            )
        except Exception as e:
            self.logger.exception('failed POST to airflow: %s' % e)
        else:
            self.logger.info(
                'successfully called airflow %s' % resp.text)
        return req.get_response(self.app)


def test_new_upload_trigger_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def test_new_upload_trigger_filter(app):
        return TestNewUploadTriggerMiddleware(app, conf)

    return test_new_upload_trigger_filter
