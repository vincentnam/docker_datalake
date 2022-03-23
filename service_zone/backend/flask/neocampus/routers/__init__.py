from .swift_file import swift_file_bp
from .mongo_data import mongo_data_bp
from .influxdb_data import influxdb_data_bp
from ..utils.swagger.api_spec import spec
from flask import jsonify
from ..utils.swagger.swagger import swagger_ui_blueprint, SWAGGER_URL


def init_app(app):

    # Blueprint to get Swagger UI
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    # Routers Blueprints
    app.register_blueprint(swift_file_bp, url_prefix="/api")
    app.register_blueprint(mongo_data_bp, url_prefix="/api")
    app.register_blueprint(influxdb_data_bp, url_prefix="/api")

    # Loading all functions of each Blueprint in JSON OpenAPI specifications
    with app.test_request_context():
        # Register all Swagger documented functions here
        for fn_name in app.view_functions:
            if fn_name == 'static':
                continue
            print(f"Loading swagger docs for function: {fn_name}")
            view_fn = app.view_functions[fn_name]
            spec.path(view=view_fn)

    @app.route("/api/swagger.json")
    def create_swagger_spec():
        return jsonify(spec.to_dict())