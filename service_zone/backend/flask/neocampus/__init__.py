import os
from flask import Flask
from . import routers
from flask_cors import CORS
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_pyfile("config.py")
    routers.init_app(app)

    return app
