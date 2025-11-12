"""API dependencies for authentication and database access."""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_database
from ..models.client_registration import User
from ..utils.security import verify_token


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_database)
) -> User:
    """Get current authenticated user from JWT token (header or cookie)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = None

    # Try Authorization header first
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix

    # Try cookie if no header token
    if not token:
        token = request.cookies.get("admin_token")

    if not token:
        raise credentials_exception

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    username = payload.get("sub")
    if not isinstance(username, str):
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_roles: list):
    """Role-based dependency."""
    def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_dependency


# Role requirements
admin_required = require_role(['admin'])
manager_required = require_role(['admin', 'manager'])
employee_required = require_role(['admin', 'manager', 'employee'])
shopper_required = require_role(['admin', 'manager', 'employee', 'shopper'])
customer_required = require_role(['admin', 'manager', 'employee', 'shopper', 'customer'])