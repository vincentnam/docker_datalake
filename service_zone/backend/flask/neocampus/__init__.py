import os

from flask import Flask
# from flask_keystone import FlaskKeystone
# from flask_oslolog import OsloLog
# from oslo_config import cfg
# from oslo_context import context
from . import routers

# key = FlaskKeystone()
# cfg.CONF(default_config_files=['neocampus/config.ini'])

def create_app():
    app = Flask(__name__)

#     key.init_app(app)
    app.config.from_pyfile("config.py")
    routers.init_app(app)

    return app
