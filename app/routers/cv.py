"""
CV content router.

Exposes markdown CV content through REST endpoints.

This router handles:
- Raw markdown content retrieval
- HTML rendering
- File metadata
- Error handling

Why separate CV router:
- Clean separation of concerns
- Easy to add versioning (/api/v1/cv)
- Independent testing
"""

import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.cv import CVHtmlResponse, CVRawResponse, MetadataResponse
from app.services.markdown_service import (
    MarkdownParseError,
    get_markdown_service,
)

router = APIRouter(prefix="/cv", tags=["cv"])
logger = logging.getLogger(__name__)


def _handle_parse_error(error: MarkdownParseError) -> None:
    """
    Convert markdown parse errors to HTTP exceptions.

    Args:
        error: The markdown parse error

    Raises:
        HTTPException: Appropriate HTTP error response
    """
    if "file not found" in error.message.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CV file not found: {error.message}",
        ) from error
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to process CV content: {error.message}",
    ) from error


@router.get("/raw", response_model=CVRawResponse)
async def get_raw_cv() -> CVRawResponse:
    """
    Get raw markdown content.

    Returns the unprocessed markdown content with file metadata.
    Useful for frontend that handles its own markdown rendering.

    Returns:
        CVRawResponse: Raw markdown content and metadata

    Raises:
        HTTPException: If file cannot be loaded
    """
    service = get_markdown_service()
    try:
        content, metadata_dict, parser_status = service.get_raw()
        metadata_dict["parser_status"] = parser_status
        metadata_dict["version"] = service.settings.app_version

        return CVRawResponse(
            content=content,
            metadata=MetadataResponse(**metadata_dict),
        )
    except MarkdownParseError as e:
        logger.error("Failed to get raw CV: %s", e)
        _handle_parse_error(e)


@router.get("/html", response_model=CVHtmlResponse)
async def get_html_cv() -> CVHtmlResponse:
    """
    Get rendered and sanitized HTML content.

    Returns the CV as safe HTML, ready for frontend display.
    HTML is sanitized to prevent XSS attacks.

    Returns:
        CVHtmlResponse: Rendered HTML content and metadata

    Raises:
        HTTPException: If conversion fails
    """
    service = get_markdown_service()
    try:
        html, metadata_dict, parser_status = service.get_html()
        metadata_dict["parser_status"] = parser_status
        metadata_dict["version"] = service.settings.app_version

        return CVHtmlResponse(
            content=html,
            metadata=MetadataResponse(**metadata_dict),
        )
    except MarkdownParseError as e:
        logger.error("Failed to get HTML CV: %s", e)
        _handle_parse_error(e)


@router.get("/metadata", response_model=MetadataResponse)
async def get_cv_metadata() -> MetadataResponse:
    """
    Get CV file metadata.

    Returns information about the markdown file without loading content.
    More efficient than other endpoints when only metadata is needed.

    Returns:
        MetadataResponse: File metadata

    Raises:
        HTTPException: If file cannot be accessed
    """
    service = get_markdown_service()
    try:
        metadata_dict, parser_status = service.get_metadata_only()
        if not metadata_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV file not found",
            )
        metadata_dict["parser_status"] = parser_status
        metadata_dict["version"] = service.settings.app_version

        return MetadataResponse(**metadata_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get CV metadata: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metadata: {e!s}",
        ) from e
