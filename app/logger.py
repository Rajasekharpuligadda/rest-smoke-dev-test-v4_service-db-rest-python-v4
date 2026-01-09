"""
Project logger configuration
"""

import logging

from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor


# Placeholders will be changed in further configuration
logger = logging.getLogger("placeholder")
tracer = trace.get_tracer(__name__)


def configure_logging_and_tracing(app: Flask):
    """
    Configures logging and OpenTelemetry tracing using the app's settings.
    This function should be called once from the create_app factory.
    """
    settings = app.extensions.get("settings")
    if not settings:
        logger.error(
            "Settings object not found in app extensions. Logging setup failed."
        )
        return

    logger.name = settings.PROJECT_NAME
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if settings.OTEL_ENABLED:
        try:
            resource = Resource.create(
                {
                    ResourceAttributes.SERVICE_NAME: settings.PROJECT_NAME,
                    ResourceAttributes.SERVICE_VERSION: settings.VERSION,
                    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT,
                }
            )

            tracer_provider = TracerProvider(resource=resource)

            if hasattr(settings, "APPLICATIONINSIGHTS_CONNECTION_STRING"):
                azure_exporter = AzureMonitorTraceExporter(
                    connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING
                )
                span_processor = BatchSpanProcessor(azure_exporter)
                tracer_provider.add_span_processor(span_processor)

            trace.set_tracer_provider(tracer_provider)
            logger.info(f"Successfully initialized OpenTelemetry tracing for {settings.OTEL_PROVIDER}.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry tracing: {str(e)}")
            logger.warning("Application will continue without tracing capabilities.")

    global tracer
    tracer = trace.get_tracer(settings.PROJECT_NAME)

    logger.info("Logger and Tracer configuration complete.")
