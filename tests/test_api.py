"""
API endpoint tests.

Tests the actual FastAPI routes to ensure they:
- Return correct HTTP status codes
- Return valid response schemas
- Handle errors correctly
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(test_cv_file):
    """Create a test client with a temporary CV file."""
    from app.core.config import Settings, get_settings
    from app.services.markdown_service import get_markdown_service

    # Clear both settings and service caches
    get_settings.cache_clear()
    get_markdown_service.cache_clear()

    # Create app with test settings
    test_settings = Settings(
        app_name="Test CV API",
        app_version="1.0.0",
        app_environment="testing",
        markdown_path=test_cv_file,
        cors_origins=["http://localhost:3000"],
        log_level="WARNING",
        enable_hot_reload=False,
    )

    app = create_app(test_settings)
    yield TestClient(app)

    # Clear cache after test
    get_settings.cache_clear()
    get_markdown_service.cache_clear()


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_check_success(self, client):
        """Test health check returns correct response."""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["environment"] in ("testing", "development")
        assert "timestamp" in data


class TestCVRawEndpoint:
    """Tests for /api/cv/raw endpoint."""

    def test_get_raw_cv_success(self, client):
        """Test getting raw markdown content."""
        response = client.get("/api/cv/raw")
        assert response.status_code == 200

        data = response.json()
        assert "content" in data
        assert "metadata" in data
        assert data["metadata"]["parser_status"] == "ready"
        assert data["metadata"]["version"] == "1.0.0"

    def test_get_raw_cv_content(self, client):
        """Test raw content contains expected markdown."""
        response = client.get("/api/cv/raw")
        data = response.json()

        # Check that we get markdown content
        assert "#" in data["content"]  # Has markdown headers
        assert len(data["content"]) > 0


class TestCVHtmlEndpoint:
    """Tests for /api/cv/html endpoint."""

    def test_get_html_cv_success(self, client):
        """Test getting HTML content."""
        response = client.get("/api/cv/html")
        assert response.status_code == 200

        data = response.json()
        assert "content" in data
        assert "metadata" in data
        assert data["metadata"]["parser_status"] == "ready"

    def test_get_html_cv_contains_tags(self, client):
        """Test HTML content contains expected tags."""
        response = client.get("/api/cv/html")
        data = response.json()

        # Should contain HTML tags (note: headers have id attributes)
        assert "<h1" in data["content"]
        assert "<h2" in data["content"]

        # Should NOT contain unsafe content
        assert "<script>" not in data["content"]


class TestCVMetadataEndpoint:
    """Tests for /api/cv/metadata endpoint."""

    def test_get_metadata_success(self, client):
        """Test getting file metadata."""
        response = client.get("/api/cv/metadata")
        assert response.status_code == 200

        data = response.json()
        assert data["filename"]  # Any filename is fine
        assert data["size_bytes"] > 0
        assert "last_modified" in data
        assert data["parser_status"] == "ready"
        assert data["version"] == "1.0.0"


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns basic info."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "CV API"
        assert data["version"] == "1.0.0"
        assert data["health"] == "/api/health"


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_on_nonexistent_endpoint(self, client):
        """Test 404 response for nonexistent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
