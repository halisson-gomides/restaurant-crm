"""Template context processors."""

from fastapi import Request
from ..config import settings


def company_context(request: Request) -> dict:
    """Add company name to template context."""
    return {
        "company_name": settings.company_name,
        "company_logo": settings.company_logo,
        "app_name": settings.app_name,
        "debug": settings.debug,
        "environment": settings.environment
    }