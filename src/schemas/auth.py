"""Authentication schemas for admin login system."""

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserLogin(BaseModel):
    """Schema for user login request."""
    username: str  # CPF or CNPJ
    password: str


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "customer"


class UserOut(BaseModel):
    """Schema for user response data."""
    id: str
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool

    class Config:
        from_attributes = True