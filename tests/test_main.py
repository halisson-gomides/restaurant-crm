"""Tests for main application."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.mark.unit
def test_root_endpoint():
    """Test root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "environment" in data


@pytest.mark.unit
def test_health_check_endpoint():
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "environment" in data


@pytest.mark.unit
def test_openapi_schema():
    """Test OpenAPI schema generation."""
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
