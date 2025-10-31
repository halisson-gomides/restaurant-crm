"""Application configuration management."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/restaurant_crm",
        description="PostgreSQL database URL with async driver"
    )

    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token generation"
    )
    algorithm: str = Field(
        default="HS256",
        description="Algorithm for JWT token encoding"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )

    # Application Configuration
    app_name: str = Field(
        default="Restaurant CRM",
        description="CRM para Restaurantes"
    )
    company_name: str = Field(
        default="CompraJá!",
        description="Nome da empresa cliente"
    )
    debug: bool = Field(
        default=True,
        description="Debug mode flag"
    )
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )

    # CORS Configuration
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8001"],
        description="Allowed CORS origins"
    )

    # API Configuration
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="API v1 prefix"
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False
        extra = "allow"


# Global settings instance
settings = Settings()
