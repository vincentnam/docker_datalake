from .swift_file import swift_file_bp


def init_app(app):
    app.register_blueprint(swift_file_bp)
