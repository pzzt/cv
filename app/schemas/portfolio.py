"""
Pydantic schemas for portfolio/structured data.

Matches the frontend's expected CONTENT_API structure.
"""

from pydantic import BaseModel


class ExperienceEntry(BaseModel):
    """Single experience entry."""

    role: str
    company: str
    period: str
    status: str  # ACTIVE or ARCHIVED
    contributions: list[str]


class SkillCategory(BaseModel):
    """Single skill category."""

    category: str
    tagClass: str  # tag-blue, tag-green, tag-amber
    items: list[str]


class ProjectEntry(BaseModel):
    """Single project entry."""

    title: str
    architecture: str
    tooling: list[str]
    challenge: str
    solution: str
    tagClass: str


class ContactInfo(BaseModel):
    """Contact information."""

    email: str
    github: str
    linkedin: str
    pgp: str
