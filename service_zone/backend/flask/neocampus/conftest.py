import pytest
from flask import Flask
from . import routers

@pytest.fixture
def app():
    app = Flask(__name__)

    app.config.from_pyfile("config.py")
    routers.init_app(app)

    return app

@pytest.fixture
def client(app):
    return app.test_client()