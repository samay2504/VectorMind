"""
Test configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create FastAPI test client"""
    from src.api.main import create_app
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "This is a test document for the RAG system. It contains multiple sentences."


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing"""
    return {
        "source": "test",
        "author": "test_user",
        "created_at": "2024-01-01"
    }
