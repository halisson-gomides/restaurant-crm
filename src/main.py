"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import init_db, close_db, get_database
from .api.v1.registration import router as registration_router
from .utils.templates import company_context


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

# Include API routers
app.include_router(registration_router)

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
    if registration_type == "CNPJ":
        # Get CNPJ registration details
        registration = await service.cnpj_service.get_by_id(db, registration_id)
        registration_data = {
            "razao_social": registration.razao_social if registration else None,
            "cnpj": registration.cnpj if registration else None,
            "email": registration.email if registration else None,
        }
    else:
        # Get CPF registration details
        registration = await service.cpf_service.get_by_id(db, registration_id)
        registration_data = {
            "nome_completo": registration.nome_completo if registration else None,
            "cpf": registration.cpf if registration else None,
            "email": registration.email if registration else None,
        }
    
    return templates.TemplateResponse("registration/success.html", {
        "request": request,
        "registration_type": registration_type,
        "registration_id": registration_id,
        "registration_data": registration_data,
        "created_at": "Hoje",  # You might want to format this properly
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
    )
