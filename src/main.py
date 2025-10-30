"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db, close_db


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
    description="A comprehensive CRM system for restaurant chains",
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


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": "0.1.0",
        "environment": settings.environment,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.environment,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
    )
