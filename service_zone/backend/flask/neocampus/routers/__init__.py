from .swift_file import swift_file_bp
from .mongo_data import mongo_data_bp
from .influxdb_data import influxdb_data_bp


def init_app(app):
    app.register_blueprint(swift_file_bp)
    app.register_blueprint(mongo_data_bp)
    app.register_blueprint(influxdb_data_bp)