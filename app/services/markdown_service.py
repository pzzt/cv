"""
Markdown parsing and processing service.

Handles all markdown-related operations including:
- File loading and caching
- Markdown to HTML conversion
- HTML sanitization
- File metadata extraction
- Hot-reload on file changes

Why a separate service:
- Business logic separation from routes
- Testable in isolation
- Easy to swap markdown implementation
- Caching and performance optimization
"""

import hashlib
import logging
from datetime import UTC, datetime
from enum import StrEnum
from functools import lru_cache

from markdown import markdown
from nh3 import clean

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class ParserStatus(StrEnum):
    """Markdown parser status indicators."""

    READY = "ready"
    FILE_NOT_FOUND = "file_not_found"
    PARSE_ERROR = "parse_error"
    SANITIZATION_ERROR = "sanitization_error"


class MarkdownParseError(Exception):
    """Raised when markdown parsing fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class MarkdownService:
    """
    Service for markdown content processing.

    Features:
    - Lazy loading with caching
    - HTML sanitization via nh3 (rust-based, fast)
    - File metadata extraction
    - Optional hot-reload for development

    Why nh3 for sanitization:
    - Rust-based, much faster than Python bleach
    - Actively maintained security focus
    - Follows OWASP recommendations
    """

    def __init__(self, settings: Settings | None = None) -> None:
        """
        Initialize the markdown service.

        Args:
            settings: Application settings. Uses get_settings() if None.
        """
        self.settings = settings or get_settings()
        self._markdown_path = self.settings.markdown_path
        self._cached_hash: str | None = None
        self._cached_content: str | None = None
        self._cached_html: str | None = None
        self._last_load_time: datetime | None = None

    def _compute_file_hash(self, content: str) -> str:
        """
        Compute SHA256 hash of file content.

        Used for cache invalidation detection.

        Args:
            content: File content to hash

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_file_metadata(self, content: str) -> dict:
        """
        Extract metadata from markdown file.

        Args:
            content: Raw markdown content

        Returns:
            Dictionary with file metadata
        """
        try:
            stat = self._markdown_path.stat()
            return {
                "filename": self._markdown_path.name,
                "path": str(self._markdown_path.absolute()),
                "size_bytes": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=UTC),
                "content_length": len(content),
                "line_count": content.count("\n") + 1,
            }
        except OSError as e:
            logger.error("Failed to get file metadata: %s", e)
            raise MarkdownParseError("Failed to read file metadata", e) from e

    def _sanitize_html(self, html: str) -> str:
        """
        Sanitize HTML to prevent XSS attacks.

        Uses nh3 with conservative settings:
        - Allows basic formatting tags
        - Blocks scripts, iframes, forms
        - Removes dangerous attributes

        Args:
            html: Raw HTML from markdown conversion

        Returns:
            Sanitized HTML string

        Raises:
            MarkdownParseError: If sanitization fails
        """
        try:
            # Conservative tag list for safety
            return clean(
                html,
                tags={
                    "p",
                    "br",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "strong",
                    "em",
                    "u",
                    "s",
                    "a",
                    "ul",
                    "ol",
                    "li",
                    "code",
                    "pre",
                    "blockquote",
                    "hr",
                    "table",
                    "thead",
                    "tbody",
                    "tr",
                    "th",
                    "td",
                },
                attributes={
                    "a": {"href", "title"},
                    "*": {"id", "class"},
                },
                url_schemes={"https", "http", "mailto"},
                strip_comments=True,
            )
        except Exception as e:
            logger.error("HTML sanitization failed: %s", e)
            raise MarkdownParseError("Failed to sanitize HTML content", e) from e

    def load_raw(self) -> tuple[str, dict]:
        """
        Load raw markdown content from file.

        Returns:
            Tuple of (content, metadata)

        Raises:
            MarkdownParseError: If file cannot be read
        """
        try:
            content = self._markdown_path.read_text(encoding="utf-8")
            metadata = self._get_file_metadata(content)

            # Update cache if hot-reload is enabled
            if self.settings.enable_hot_reload:
                current_hash = self._compute_file_hash(content)
                if self._cached_hash != current_hash:
                    self._cached_hash = current_hash
                    self._cached_content = content
                    self._cached_html = None  # Invalidate HTML cache
                    self._last_load_time = datetime.now(tz=UTC)
                    logger.info("Markdown file reloaded: %s", self._markdown_path)

            return content, metadata
        except FileNotFoundError as e:
            logger.error("Markdown file not found: %s", self._markdown_path)
            raise MarkdownParseError(
                f"Markdown file not found: {self._markdown_path}",
                e,
            ) from e
        except OSError as e:
            logger.error("Failed to read markdown file: %s", e)
            raise MarkdownParseError("Failed to read markdown file", e) from e

    def convert_to_html(self, content: str) -> str:
        """
        Convert markdown content to sanitized HTML.

        Args:
            content: Raw markdown content

        Returns:
            Sanitized HTML string

        Raises:
            MarkdownParseError: If conversion or sanitization fails
        """
        try:
            # Convert markdown to HTML using python-markdown
            raw_html = markdown(
                content,
                extensions=[
                    "markdown.extensions.extra",
                    "markdown.extensions.codehilite",
                    "markdown.extensions.toc",
                    "markdown.extensions.nl2br",
                    "markdown.extensions.sane_lists",
                ],
                extension_configs={
                    "codehilite": {
                        "linenums": False,
                        "css_class": "highlight",
                    },
                },
            )
            return self._sanitize_html(raw_html)
        except Exception as e:
            logger.error("Markdown conversion failed: %s", e)
            raise MarkdownParseError("Failed to convert markdown to HTML", e) from e

    def get_raw(self) -> tuple[str, dict, str]:
        """
        Get raw markdown content with metadata.

        Returns:
            Tuple of (content, metadata_dict, parser_status)

        Raises:
            MarkdownParseError: If loading fails
        """
        content, metadata = self.load_raw()
        return content, metadata, ParserStatus.READY

    def get_html(self) -> tuple[str, dict, str]:
        """
        Get converted and sanitized HTML with metadata.

        Returns:
            Tuple of (html_content, metadata_dict, parser_status)

        Raises:
            MarkdownParseError: If conversion fails
        """
        content, metadata = self.load_raw()

        # Check HTML cache
        if self._cached_html and self.settings.enable_hot_reload:
            html = self._cached_html
        else:
            html = self.convert_to_html(content)
            if self.settings.enable_hot_reload:
                self._cached_html = html

        return html, metadata, ParserStatus.READY

    def get_metadata_only(self) -> tuple[dict, str]:
        """
        Get file metadata without loading full content.

        More efficient than get_raw() when only metadata is needed.

        Returns:
            Tuple of (metadata_dict, parser_status)

        Raises:
            MarkdownParseError: If file cannot be accessed
        """
        try:
            stat = self._markdown_path.stat()
            metadata = {
                "filename": self._markdown_path.name,
                "path": str(self._markdown_path.absolute()),
                "size_bytes": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=UTC),
                "content_length": stat.st_size,  # Approximate
                "line_count": 0,  # Not reading file
            }
            return metadata, ParserStatus.READY
        except FileNotFoundError:
            return {}, ParserStatus.FILE_NOT_FOUND
        except OSError as e:
            logger.error("Failed to access markdown file: %s", e)
            return {}, ParserStatus.PARSE_ERROR


@lru_cache
def get_markdown_service() -> MarkdownService:
    """
    Cached markdown service instance.

    Why cache:
    - Reuse service instance across requests
    - Maintains file content cache
    - Settings don't change during runtime

    Returns:
        MarkdownService: Singleton service instance
    """
    return MarkdownService()
