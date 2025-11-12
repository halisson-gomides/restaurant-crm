"""Authentication API routes for admin login system."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from ..database import get_database
from ..models.client_registration import User, CNPJRegistration, CPFRegistration, Organization
from ..schemas.auth import UserLogin, Token
from ..utils.security import create_access_token, verify_token
from ..api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_database)
):
    """Authenticate admin user and return access token."""
    # Find user by username (CPF/CNPJ)
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password (using simple hash for now)
    import hashlib
    salt = "restaurant_crm_salt"
    hashed_password = hashlib.sha256(f"{user_data.password}{salt}".encode()).hexdigest()

    if user.hashed_password != hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active and admin
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=60)  # 1 hour for admin sessions
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
        "is_active": current_user.is_active
    }


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_database),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get dashboard statistics for admin."""
    # Verify token
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    # Check if user is admin
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Get statistics
    cnpj_count = await db.execute(
        select(func.count()).select_from(CNPJRegistration)
    )
    total_cnpj = cnpj_count.scalar()

    cpf_count = await db.execute(
        select(func.count()).select_from(CPFRegistration)
    )
    total_cpf = cpf_count.scalar()

    org_count = await db.execute(
        select(func.count()).select_from(Organization)
    )
    total_orgs = org_count.scalar()

    user_count = await db.execute(
        select(func.count()).select_from(User)
    )
    total_users = user_count.scalar()

    # Get recent registrations (last 5)
    recent_cnpj = await db.execute(
        select(CNPJRegistration.id, CNPJRegistration.razao_social.label("name"),
               CNPJRegistration.email, CNPJRegistration.created_at)
        .order_by(CNPJRegistration.created_at.desc())
        .limit(3)
    )
    recent_cpf = await db.execute(
        select(CPFRegistration.id, CPFRegistration.nome_completo.label("name"),
               CPFRegistration.email, CPFRegistration.created_at)
        .order_by(CPFRegistration.created_at.desc())
        .limit(3)
    )

    recent_registrations = []

    # Combine and sort recent registrations
    for reg in recent_cnpj:
        recent_registrations.append({
            "id": reg.id,
            "name": reg.name,
            "email": reg.email,
            "type": "CNPJ",
            "created_at": reg.created_at.isoformat()
        })

    for reg in recent_cpf:
        recent_registrations.append({
            "id": reg.id,
            "name": reg.name,
            "email": reg.email,
            "type": "CPF",
            "created_at": reg.created_at.isoformat()
        })

    # Sort by creation date (most recent first)
    recent_registrations.sort(key=lambda x: x["created_at"], reverse=True)
    recent_registrations = recent_registrations[:5]

    return {
        "total_cnpj_registrations": total_cnpj,
        "total_cpf_registrations": total_cpf,
        "total_organizations": total_orgs,
        "total_users": total_users,
        "recent_registrations": recent_registrations
    }


@router.get("/registrations")
async def get_registrations(
    request: Request,
    page: int = 1,
    limit: int = 20,
    registration_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_database),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get paginated list of registrations for admin."""
    # Verify token and admin role
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    offset = (page - 1) * limit

    # Build queries for CNPJ and CPF registrations
    cnpj_query = select(
        CNPJRegistration.id,
        CNPJRegistration.razao_social.label("name"),
        CNPJRegistration.email,
        CNPJRegistration.celular.label("phone"),
        CNPJRegistration.created_at,
        func.literal("CNPJ").label("type")
    )

    cpf_query = select(
        CPFRegistration.id,
        CPFRegistration.nome_completo.label("name"),
        CPFRegistration.email,
        CPFRegistration.celular.label("phone"),
        CPFRegistration.created_at,
        func.literal("CPF").label("type")
    )

    # Apply filters
    if registration_type:
        if registration_type == "CNPJ":
            cpf_query = None
        elif registration_type == "CPF":
            cnpj_query = None

    if date_from:
        if cnpj_query is not None:
            cnpj_query = cnpj_query.where(CNPJRegistration.created_at >= date_from)
        if cpf_query is not None:
            cpf_query = cpf_query.where(CPFRegistration.created_at >= date_from)

    if date_to:
        if cnpj_query is not None:
            cnpj_query = cnpj_query.where(CNPJRegistration.created_at <= date_to)
        if cpf_query is not None:
            cpf_query = cpf_query.where(CPFRegistration.created_at <= date_to)

    if search:
        search_term = f"%{search}%"
        if cnpj_query is not None:
            cnpj_query = cnpj_query.where(
                (CNPJRegistration.razao_social.ilike(search_term)) |
                (CNPJRegistration.email.ilike(search_term))
            )
        if cpf_query is not None:
            cpf_query = cpf_query.where(
                (CPFRegistration.nome_completo.ilike(search_term)) |
                (CPFRegistration.email.ilike(search_term))
            )

    # Execute queries and combine results
    all_registrations = []

    if cnpj_query is not None:
        cnpj_result = await db.execute(cnpj_query.offset(offset).limit(limit))
        all_registrations.extend([dict(row) for row in cnpj_result])

    if cpf_query is not None:
        cpf_result = await db.execute(cpf_query.offset(offset).limit(limit))
        all_registrations.extend([dict(row) for row in cpf_result])

    # Sort combined results by creation date
    all_registrations.sort(key=lambda x: x["created_at"], reverse=True)

    # Apply pagination to combined results
    total_registrations = len(all_registrations)
    paginated_registrations = all_registrations[offset:offset + limit]

    # Calculate pagination info
    total_pages = (total_registrations + limit - 1) // limit

    return {
        "registrations": paginated_registrations,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_registrations,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "prev_num": page - 1 if page > 1 else None,
            "next_num": page + 1 if page < total_pages else None
        }
    }


@router.get("/registrations/{registration_id}")
async def get_registration_detail(
    registration_id: str,
    registration_type: str,
    db: AsyncSession = Depends(get_database),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get detailed information about a specific registration."""
    # Verify token and admin role
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if registration_type.upper() == "CNPJ":
        result = await db.execute(
            select(CNPJRegistration).where(CNPJRegistration.id == registration_id)
        )
        registration = result.scalar_one_or_none()
    elif registration_type.upper() == "CPF":
        result = await db.execute(
            select(CPFRegistration).where(CPFRegistration.id == registration_id)
        )
        registration = result.scalar_one_or_none()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid registration type"
        )

    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    return registration


@router.delete("/registrations/{registration_id}")
async def delete_registration(
    registration_id: str,
    registration_type: str,
    db: AsyncSession = Depends(get_database),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a registration (admin only)."""
    # Verify token and admin role
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if registration_type.upper() == "CNPJ":
        result = await db.execute(
            select(CNPJRegistration).where(CNPJRegistration.id == registration_id)
        )
        registration = result.scalar_one_or_none()
        if registration:
            await db.delete(registration)
            await db.commit()
    elif registration_type.upper() == "CPF":
        result = await db.execute(
            select(CPFRegistration).where(CPFRegistration.id == registration_id)
        )
        registration = result.scalar_one_or_none()
        if registration:
            await db.delete(registration)
            await db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid registration type"
        )

    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    return {"message": "Registration deleted successfully"}