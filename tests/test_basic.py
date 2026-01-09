import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import create_app


@pytest.fixture
def app() -> Flask:
    """Create and configure a new app instance for each test."""
    app = create_app()
    return app


@pytest.fixture
def client(app: Flask):
    """A test client for the app."""
    return app.test_client()


def test_health_check(client: FlaskClient):
    """Test the health check endpoint."""
    response = client.get("/service-db-rest-python-v4/health/liveness")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "UP"
    assert json_data["message"] == "Service is alive."


def test_index_route(client: FlaskClient):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Welcome to the API!"
