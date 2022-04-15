import flask
from flask_keystone import FlaskKeystone
from flask_oslolog import OsloLog
from oslo_config import cfg
from oslo_context import context

def get_oslo_context(rule, project_id):
    # headers in a specific format that oslo.context wants
    headers = {
        f'HTTP_{name.upper().replace("-", "_")}': value
        for name, value in flask.request.headers.items()
    }

    return context.RequestContext.from_environ(headers)