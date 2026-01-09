from flask import request, make_response, jsonify
from openapi_core import OpenAPI
from openapi_core.contrib.flask import FlaskOpenAPIRequest
from openapi_core.templating.paths.exceptions import PathNotFound, ServerNotFound
from pathlib import Path
from flask import Flask
from a2wsgi import WSGIMiddleware
from .routes import main as main_blueprint
from .health import health as health_blueprint
from app.settings import Settings
from .extensions.postgres import init_postgres
from app.logger import logger, configure_logging_and_tracing

def init_settings(app: Flask):
    if not hasattr(app, "extensions"):
        app.extensions = {}

    settings = Settings()
    app.config.from_object(settings)
    app.extensions["settings"] = settings

def create_app():
    """
    Flask application factory function.
    """

    app = Flask(__name__)

    ALLOWED_PATHS = ("liveness", "readiness", "favicon.co")
    spec_path = Path(__file__).parent.parent / "resources" / "user-management-openapi.json"
    if spec_path.exists():
        spec = OpenAPI.from_file_path(str(spec_path))

        @app.before_request
        def validate_request_middleware():
            if request.path.split("/")[-1] in ALLOWED_PATHS:
                return None
            try:
                spec.validate_request(FlaskOpenAPIRequest(request))
            except PathNotFound as e:
                return make_response(
                    jsonify(
                        {
                            "error": "Path not found in OpenAPI specification",
                            "details": str(e),
                        }
                    ),
                    404,
                )
            except ServerNotFound as e:
                return make_response(
                    jsonify({"error": "Server host not allowed", "details": str(e)}),
                    400,
                )
    init_settings(app)
    configure_logging_and_tracing(app)

    init_postgres(app)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(health_blueprint)

    logger.info("Flask service setup is completed.")
    return WSGIMiddleware(app)
