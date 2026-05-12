"""
Pytest configuration and fixtures.

Shared test setup for all test modules.
"""

import sys
from pathlib import Path

import pytest

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """# Test CV

## Profile

A test profile.

## Skills

- Skill 1
- Skill 2

[Link](https://example.com)
"""


@pytest.fixture
def sample_html():
    """Sample expected HTML output."""
    return "<h1>Test CV</h1>"


@pytest.fixture
def mock_settings():
    """Mock application settings for testing."""
    from app.core.config import Settings

    return Settings(
        app_name="Test CV API",
        app_version="1.0.0",
        app_environment="testing",
        markdown_path=Path("tests/fixtures/test_cv.md"),
        cors_origins=["http://localhost:3000"],
        log_level="INFO",
        enable_hot_reload=False,
    )


@pytest.fixture
def test_cv_file(tmp_path, sample_markdown):
    """Create a temporary CV file for testing."""
    cv_file = tmp_path / "test_cv.md"
    cv_file.write_text(sample_markdown)
    return cv_file
