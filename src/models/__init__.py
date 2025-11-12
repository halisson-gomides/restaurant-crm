"""Database models package."""

from .base import Base, BaseModel

# Import all models to ensure Alembic can find them
from .client_registration import (
    Address,
    RegistrationSession,
    CNPJRegistration,
    CPFRegistration,
    Organization,
    User,
    UserRole,
)

__all__ = [
    "Base",
    "BaseModel",
    "Address",
    "RegistrationSession",
    "CNPJRegistration",
    "CPFRegistration",
    "Organization",
    "User",
    "UserRole",
]
