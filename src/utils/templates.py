"""Template context processors."""

from fastapi import Request
from fastapi.templating import Jinja2Templates
from ..config import settings
from .helpers import remove_accents


# Initialize templates
templates = Jinja2Templates(directory="templates")

# Add custom Jinja2 filters
templates.env.filters['remove_accents'] = remove_accents


def company_context(request: Request) -> dict:
    """Add company name to template context."""
    return {
        "company_name": settings.company_name,
        "company_logo": settings.company_logo,
        "app_name": settings.app_name,
        "debug": settings.debug,
        "environment": settings.environment
    }