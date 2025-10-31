"""
Integration test for ingestion pipeline
"""

import pytest


def test_health_endpoint(test_client):
    """Test health endpoint"""
    response = test_client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(test_client):
    """Test root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


@pytest.mark.skip(reason="Requires running services")
def test_readiness_check(test_client):
    """Test readiness check"""
    response = test_client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "dependencies" in data
