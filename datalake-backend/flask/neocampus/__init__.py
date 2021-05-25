import os

from flask import Flask
from flask_cors import CORS
from . import routers


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_pyfile("config.py")
    routers.init_app(app)

    return app
