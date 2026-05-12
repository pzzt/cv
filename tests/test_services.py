"""
Service layer tests.

Tests the business logic in isolation from FastAPI.
"""

from pathlib import Path

import pytest

from app.services.markdown_service import (
    MarkdownParseError,
    MarkdownService,
    ParserStatus,
)


class TestMarkdownService:
    """Tests for MarkdownService."""

    def test_load_valid_file(self, test_cv_file):
        """Test loading a valid markdown file."""
        from app.core.config import Settings

        settings = Settings(markdown_path=test_cv_file)
        service = MarkdownService(settings)

        content, metadata, status = service.get_raw()

        assert status == ParserStatus.READY
        assert "# Test CV" in content
        assert metadata["filename"] == test_cv_file.name
        assert metadata["size_bytes"] > 0

    def test_convert_to_html(self, test_cv_file):
        """Test markdown to HTML conversion."""
        from app.core.config import Settings

        settings = Settings(markdown_path=test_cv_file)
        service = MarkdownService(settings)

        html, metadata, status = service.get_html()

        assert status == ParserStatus.READY
        assert "<h1" in html  # Headers have id attributes
        assert "<h2" in html

    def test_html_sanitization(self, tmp_path):
        """Test that dangerous HTML is sanitized."""
        # Create file with malicious content
        malicious_file = tmp_path / "malicious.md"
        malicious_file.write_text(
            "# Test\n\n<script>alert('xss')</script>\n\n[Click](javascript:alert('xss'))"
        )

        from app.core.config import Settings

        settings = Settings(markdown_path=malicious_file)
        service = MarkdownService(settings)

        html, _, _ = service.get_html()

        # Script tags should be removed
        assert "<script>" not in html
        assert "javascript:" not in html

    def test_file_not_found_error(self):
        """Test error handling when file doesn't exist."""
        from app.core.config import Settings

        settings = Settings(markdown_path=Path("nonexistent.md"))
        service = MarkdownService(settings)

        with pytest.raises(MarkdownParseError) as exc_info:
            service.get_raw()

        assert "file not found" in str(exc_info.value).lower()

    def test_get_metadata_only(self, test_cv_file):
        """Test getting metadata without loading content."""
        from app.core.config import Settings

        settings = Settings(markdown_path=test_cv_file)
        service = MarkdownService(settings)

        metadata, status = service.get_metadata_only()

        assert status == ParserStatus.READY
        assert metadata["filename"] == test_cv_file.name
        assert metadata["size_bytes"] > 0

    def test_link_sanitization(self, tmp_path):
        """Test that links are properly sanitized."""
        link_file = tmp_path / "links.md"
        link_file.write_text(
            "[Safe](https://example.com) [FTP](ftp://example.com) [Javascript](javascript:alert(1))"
        )

        from app.core.config import Settings

        settings = Settings(markdown_path=link_file)
        service = MarkdownService(settings)

        html, _, _ = service.get_html()

        # HTTPS links should be allowed
        assert 'href="https://example.com"' in html

        # FTP and javascript should be removed/not allowed
        assert "ftp://" not in html
        assert "javascript:" not in html
