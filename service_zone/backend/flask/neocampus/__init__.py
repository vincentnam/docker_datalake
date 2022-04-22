import os
from flask import Flask
from . import routers

def create_app():
    app = Flask(__name__)

    app.config.from_pyfile("config.py")
    routers.init_app(app)

    return app
