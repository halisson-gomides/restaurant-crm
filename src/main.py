"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import init_db, close_db, get_database
from .api.v1.registration import router as registration_router
from .api.auth import router as auth_router
from .utils.templates import company_context
from .utils.helpers import remove_accents
from pathlib import Path


def format_brazilian_datetime(dt) -> str:
    """
    Format datetime to Brazilian Portuguese format with timezone.
    
    Args:
        dt: Datetime object or SQLAlchemy column to format
        
    Returns:
        Formatted date string in pt-BR format
    """
    # Handle SQLAlchemy column objects
    if hasattr(dt, 'expression'):
        # If it's a SQLAlchemy column, use current time
        dt = datetime.now(timezone.utc)
    elif not isinstance(dt, datetime):
        # If it's not a datetime, use current time
        dt = datetime.now(timezone.utc)
    
    # Brazilian timezone (America/Sao_Paulo - UTC-3)
    brazil_tz = ZoneInfo('America/Sao_Paulo')
    
    # Convert to Brazilian timezone if naive datetime
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(brazil_tz)
    else:
        dt = dt.astimezone(brazil_tz)
    
    # Format as "dd de MMMM de yyyy às HH:mm"
    months = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }
    
    day = dt.day
    month = months[dt.month]
    year = dt.year
    hour = dt.hour
    minute = dt.minute
    
    return f"{day} de {month} de {year} às {hour:02d}:{minute:02d}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events.

    Args:
        app: FastAPI application instance.

    Yields:
        None
    """
    # Startup
    print(f"Starting {settings.app_name} in {settings.environment} mode...")
    await init_db()
    print("Database initialized successfully")

    yield

    # Shutdown
    print("Shutting down application...")
    await close_db()
    print("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A comprehensive CRM system for restaurant chains with CNPJ/CPF registration",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Initialize templates
templates = Jinja2Templates(directory="templates")

# Add custom Jinja2 filters
templates.env.filters['remove_accents'] = remove_accents

# Include API routers
app.include_router(registration_router)
app.include_router(auth_router)

# Homepage route
@app.get("/", tags=["Pages"])
async def home(request: Request):
    """Homepage."""
    return templates.TemplateResponse("registration/select_type.html", {
        "request": request,
        **company_context(request)
    })

# Registration page routes
@app.get("/registration", tags=["Pages"])
async def registration_page(request: Request):
    """Registration type selection page."""
    return templates.TemplateResponse("registration/select_type.html", {
        "request": request,
        **company_context(request)
    })

@app.get("/registration/cnpj/{session_id}", tags=["Pages"])
async def cnpj_registration_page(request: Request, session_id: str):
    """CNPJ registration page."""
    return templates.TemplateResponse("registration/cnpj.html", {
        "request": request,
        "session_id": session_id,
        **company_context(request)
    })

@app.get("/registration/cpf/{session_id}", tags=["Pages"])
async def cpf_registration_page(request: Request, session_id: str):
    """CPF registration page."""
    return templates.TemplateResponse("registration/cpf.html", {
        "request": request,
        "session_id": session_id,
        **company_context(request)
    })

# Admin authentication routes
@app.get("/auth/login", tags=["Admin Pages"])
async def admin_login_page(request: Request):
    """Admin login page."""
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        **company_context(request)
    })

@app.get("/auth/dashboard", tags=["Admin Pages"])
async def admin_dashboard_page(request: Request):
    """Admin dashboard page."""
    # Check if user is authenticated (this would be handled by middleware in production)
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": {"first_name": "System", "last_name": "Administrator"},
        "company_name": "Restaurant CRM",
        **company_context(request)
    })

@app.get("/auth/registrations", tags=["Admin Pages"])
async def admin_registrations_page(request: Request):
    """Admin registrations management page."""
    return templates.TemplateResponse("admin/registrations.html", {
        "request": request,
        "user": {"first_name": "System", "last_name": "Administrator"},
        "company_name": "Restaurant CRM",
        **company_context(request)
    })


@app.get("/registration/success/{registration_type}/{registration_id}", tags=["Pages"])
async def registration_success(
    request: Request,
    registration_type: str,
    registration_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Registration success page."""
    from .services.client_registration_service import ClientRegistrationService
    
    # Get registration data for display
    service = ClientRegistrationService()
    registration = None
    created_at = datetime.now(timezone.utc)
    
    if registration_type == "CNPJ":
        # Get CNPJ registration details
        registration = await service.cnpj_service.get_by_id(db, registration_id)
        registration_data = {
            "razao_social": registration.razao_social if registration else None,
            "cnpj": registration.cnpj if registration else None,
            "email": registration.email if registration else None,
        }
        if registration:
            created_at = registration.created_at
    else:
        # Get CPF registration details
        registration = await service.cpf_service.get_by_id(db, registration_id)
        registration_data = {
            "nome_completo": registration.nome_completo if registration else None,
            "cpf": registration.cpf if registration else None,
            "email": registration.email if registration else None,
        }
        if registration:
            created_at = registration.created_at
    
    # Format the created_at date in Brazilian Portuguese
    formatted_date = format_brazilian_datetime(created_at)
    
    return templates.TemplateResponse("registration/success.html", {
        "request": request,
        "registration_type": registration_type,
        "registration_id": registration_id,
        "registration_data": registration_data,
        "created_at": formatted_date,
        **company_context(request)
    })

# API Routes
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.environment,
        "version": "0.1.0",
    }

# HTMX specific endpoints
@app.get("/health/htmx", tags=["Health"])
async def htmx_health():
    """HTMX health check endpoint."""
    return {"status": "ok", "htmx": True}

# API Documentation endpoint
@app.get("/docs", tags=["Documentation"])
async def api_docs():
    """Redirect to API documentation."""
    return {"redirect": "/docs", "message": "API documentation available at /docs"}


@app.get("/download/politica-de-privacidade", name="download_privacy_policy")
async def download_privacy_policy():
    """
    Serve o arquivo de política de privacidade para download.
    """
    from pathlib import Path
    
    # Caminho para o arquivo de política de privacidade
    file_path = Path("docs/politica_de_privacidade.pdf")
    
    # Nome que o arquivo terá ao ser baixado pelo usuário
    download_name = "Política de Privacidade.pdf"

    # Verificação de segurança: checa se o arquivo existe
    if not file_path.exists():
        return {"error": "Arquivo não encontrado"}, 404

    # Retorna o arquivo como um download
    return FileResponse(
        path=file_path,
        filename=download_name,
        media_type='application/pdf'
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
    )
