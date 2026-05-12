"""
Portfolio data service.

Loads and serves structured portfolio data from JSON file.
"""

import json
import logging

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for loading portfolio data."""

    def __init__(self, settings: Settings | None = None) -> None:
        """
        Initialize the portfolio service.

        Args:
            settings: Application settings. Uses get_settings() if None.
        """
        self.settings = settings or get_settings()
        self._portfolio_path = self.settings.markdown_path.parent / "portfolio.json"
        self._cached_data: dict | None = None

    def load_portfolio(self) -> dict:
        """
        Load portfolio data from JSON file.

        Returns:
            Dictionary with portfolio data

        Raises:
            FileNotFoundError: If portfolio file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        if self._cached_data:
            return self._cached_data

        try:
            with open(self._portfolio_path, encoding="utf-8") as f:
                self._cached_data = json.load(f)
            logger.info("Portfolio data loaded from: %s", self._portfolio_path)
            return self._cached_data
        except FileNotFoundError:
            logger.error("Portfolio file not found: %s", self._portfolio_path)
            raise
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in portfolio file: %s", e)
            raise

    def get_experience(self) -> list:
        """Get experience entries."""
        return self.load_portfolio().get("experience", [])

    def get_skills(self) -> list:
        """Get skill categories."""
        return self.load_portfolio().get("skills", [])

    def get_projects(self) -> list:
        """Get project entries."""
        return self.load_portfolio().get("projects", [])

    def get_contact(self) -> dict:
        """Get contact information."""
        return self.load_portfolio().get("contact", {})


def get_portfolio_service() -> PortfolioService:
    """
    Get portfolio service instance.

    Returns:
        PortfolioService: Service instance
    """
    return PortfolioService()
