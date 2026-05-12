"""
Portfolio router.

Exposes structured portfolio data for the frontend.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from app.services.portfolio_service import get_portfolio_service

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
logger = logging.getLogger(__name__)


@router.get("/experience")
async def get_experience() -> dict:
    """
    Get work experience entries.

    Returns:
        List of experience entries with role, company, period, status, contributions
    """
    service = get_portfolio_service()
    try:
        return {"experience": service.get_experience()}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio data not found",
        ) from None
    except Exception as e:
        logger.error("Failed to get experience: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load experience data",
        ) from e


@router.get("/skills")
async def get_skills() -> dict:
    """
    Get skills by category.

    Returns:
        List of skill categories with items and tag styling
    """
    service = get_portfolio_service()
    try:
        return {"skills": service.get_skills()}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio data not found",
        ) from None
    except Exception as e:
        logger.error("Failed to get skills: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load skills data",
        ) from e


@router.get("/projects")
async def get_projects() -> dict:
    """
    Get project entries.

    Returns:
        List of projects with architecture, tooling, challenges, solutions
    """
    service = get_portfolio_service()
    try:
        return {"projects": service.get_projects()}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio data not found",
        ) from None
    except Exception as e:
        logger.error("Failed to get projects: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load projects data",
        ) from e


@router.get("/contact")
async def get_contact() -> dict:
    """
    Get contact information.

    Returns:
        Contact info with email, github, linkedin, pgp
    """
    service = get_portfolio_service()
    try:
        return service.get_contact()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio data not found",
        ) from None
    except Exception as e:
        logger.error("Failed to get contact: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load contact data",
        ) from e


@router.get("/")
async def get_all() -> dict:
    """
    Get all portfolio data in one request.

    Returns:
        Complete portfolio data object matching frontend's CONTENT_API structure
    """
    service = get_portfolio_service()
    try:
        return service.load_portfolio()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio data not found",
        ) from None
    except Exception as e:
        logger.error("Failed to get portfolio: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load portfolio data",
        ) from e
