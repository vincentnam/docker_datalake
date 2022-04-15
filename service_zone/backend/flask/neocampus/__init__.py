import os

from flask import Flask
from flask_keystone import FlaskKeystone
from flask_oslolog import OsloLog
from oslo_config import cfg
from oslo_context import context
from . import routers

key = FlaskKeystone()
log = OsloLog()
cfg.CONF(default_config_files=['config.ini'])

def create_app():
    app = Flask(__name__)

    log.init_app(app)
    key.init_app(app)
    app.config.from_pyfile("config.py")
    routers.init_app(app)

    return app
