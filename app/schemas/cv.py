"""
Pydantic schemas for CV-related API responses.

These schemas define the contract between the backend and frontend.
They provide:
- Type validation for API responses
- Automatic OpenAPI documentation
- Serialization/deserialization logic
- Clear API contract documentation

Why separate schemas:
- Decouples domain models from API contracts
- Allows API versioning without changing business logic
- Enables response filtering and transformation
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(
        default="healthy",
        description="Service health status",
    )
    version: str = Field(
        description="Application version",
    )
    environment: str = Field(
        description="Current environment (development, staging, production)",
    )
    timestamp: datetime = Field(
        default_factory=_utc_now,
        description="Response timestamp in UTC",
    )


class MetadataResponse(BaseModel):
    """CV file metadata response schema."""

    filename: str = Field(description="Name of the markdown file")
    path: str = Field(description="Full path to the markdown file")
    size_bytes: int = Field(description="File size in bytes")
    last_modified: datetime = Field(description="Last modification timestamp (UTC)")
    parser_status: str = Field(description="Markdown parser status")
    content_length: int = Field(description="Character count of raw content")
    line_count: int = Field(description="Number of lines in the file")
    version: str = Field(description="Application version")


class CVRawResponse(BaseModel):
    """Raw markdown content response schema."""

    content: str = Field(description="Raw markdown content")
    metadata: MetadataResponse = Field(description="File metadata")


class CVHtmlResponse(BaseModel):
    """Rendered HTML content response schema."""

    content: str = Field(description="Sanitized HTML content")
    metadata: MetadataResponse = Field(description="File metadata")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(description="Error type/category")
    message: str = Field(description="Human-readable error message")
    detail: str | None = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=_utc_now)
