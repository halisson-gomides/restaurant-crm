# Restaurant CRM - Software Architecture Document
**For Senior Python Developer Implementation**

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Principles](#architecture-principles)
3. [System Architecture](#system-architecture)
4. [Database Design](#database-design)
5. [API Design](#api-design)
6. [Stage 1: Initial Project Setup](#stage-1-initial-project-setup)
7. [Stage 2: Client Form Register](#stage-2-client-form-register)
8. [Stage 3: Authentication System](#stage-3-authentication-system)
9. [Stage 4: Restaurant Shopping List](#stage-4-restaurant-shopping-list)
10. [Development Guidelines](#development-guidelines)

---

## Project Overview

### Purpose
Build a comprehensive CRM system for restaurant chains with multi-location support, focusing on shopping list management, inventory control, and operational efficiency.

### Target Users
- **Administrators**: System configuration and user management (desktop focus)
- **Managers**: Shopping list creation and inventory oversight (desktop primary, mobile accessible)
- **Employees**: Order processing and inventory updates (mobile and desktop support)
- **Shoppers**: Mobile-optimized shopping list management (mobile-first design)
- **Customers**: Corporate restaurant companies using the system (desktop focus)

### Critical Responsive Design Requirements
- **Mobile-First Approach**: All interfaces must be designed starting from mobile screen sizes
- **Cross-Device Compatibility**: Seamless experience across smartphones, tablets, and desktops
- **Touch-Optimized**: All interactive elements must be touch-friendly (minimum 44px touch targets)
- **Responsive Data Tables**: Large datasets must remain usable on small screens
- **Offline-First**: Shopper interface must work reliably with intermittent connectivity
- **Performance**: Fast loading on mobile networks and low-end devices

---

## Architecture Principles

### Core Principles
1. **Clean Architecture**: Separation of concerns with clear layers
2. **Domain-Driven Design**: Business logic organized around domain entities
3. **Async-First**: All database operations are asynchronous
4. **Test-Driven Development**: Comprehensive test coverage for all features
5. **Security by Design**: Role-based access control from the ground up

### Technology Stack
- **Backend**: Python 3.12+ with FastAPI
- **Database**: PostgreSQL 17 with async operations
- **Frontend**: Jinja2 templates + HTMX for interactivity
- **ORM**: SQLAlchemy (async) for data access
- **Authentication**: Session-based with JWT tokens
- **Validation**: Pydantic models
- **Testing**: Pytest with async support

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Admin     │  │   Manager   │  │   Shopper   │        │
│  │   UI        │  │   UI        │  │   UI        │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Jinja2 + HTMX Templates                │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                   FastAPI Server                    │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │  │
│  │  │ Auth Routes │ │ CRUD Routes │ │ Business    │    │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Business Logic Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Auth      │  │ Shopping    │  │ Client      │        │
│  │  Service    │  │  Service    │  │ Service     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Access Layer                         │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              SQLAlchemy Async Models                │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                PostgreSQL 17                        │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Design

### Core Entities

#### Organizations (Companies)
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    trade_name VARCHAR(255),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(20) UNIQUE NOT NULL, -- CPF or CNPJ
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager', 'employee', 'shopper', 'customer')),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### User Roles (for multi-role support)
```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    role VARCHAR(20) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Categories
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Shopping Items Catalog
```sql
CREATE TABLE shopping_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    category_id UUID REFERENCES categories(id),
    description TEXT,
    default_unit VARCHAR(20), -- 'kg', 'g', 'l', 'ml', 'unidade', 'pacote', 'caixa', etc.
    estimated_price DECIMAL(10,2), -- Estimated price for reference
    barcode VARCHAR(50), -- For future barcode scanning feature
    is_active BOOLEAN DEFAULT TRUE,
    usage_frequency INTEGER DEFAULT 0, -- How often this item appears in shopping lists
    created_by UUID REFERENCES users(id), -- Who added this item
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure unique names per category to prevent duplicates
    UNIQUE(name, category_id)
);
```

#### Supermarkets
```sql
CREATE TABLE supermarkets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Shopping Lists
```sql
CREATE TABLE shopping_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed')),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Shopping List Items
```sql
CREATE TABLE shopping_list_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shopping_list_id UUID REFERENCES shopping_lists(id),
    shopping_item_id UUID REFERENCES shopping_items(id), -- References catalog item
    quantity DECIMAL(10,2),
    unit VARCHAR(20), -- Can override the default unit from catalog
    estimated_price DECIMAL(10,2), -- User's estimated price for this specific list
    actual_price DECIMAL(10,2), -- Real price found while shopping
    notes TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    added_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure unique items per shopping list (prevent duplicates)
    UNIQUE(shopping_list_id, shopping_item_id)
);
```

#### Custom Items (for items not in catalog)
```sql
CREATE TABLE custom_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shopping_list_item_id UUID REFERENCES shopping_list_items(id) ON DELETE CASCADE,
    original_name VARCHAR(255) NOT NULL, -- The custom name provided by user
    category_id UUID REFERENCES categories(id), -- Suggested category for the item
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Item Prices (for price comparison)
```sql
CREATE TABLE item_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shopping_list_item_id UUID REFERENCES shopping_list_items(id),
    supermarket_id UUID REFERENCES supermarkets(id),
    price DECIMAL(10,2) NOT NULL,
    price_per_unit DECIMAL(10,4), -- Price per unit for better comparison
    unit_used VARCHAR(20), -- Unit used for this price (kg, unidade, etc.)
    checked_by UUID REFERENCES users(id),
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_available BOOLEAN DEFAULT TRUE, -- Whether item is currently available

    -- Track price history
    UNIQUE(shopping_list_item_id, supermarket_id, checked_at)
);
```

#### Item Usage Statistics (for analytics and recommendations)
```sql
CREATE TABLE item_usage_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shopping_item_id UUID REFERENCES shopping_items(id),
    organization_id UUID REFERENCES organizations(id),
    total_used INTEGER DEFAULT 0, -- Total times this item was used
    avg_quantity DECIMAL(10,2), -- Average quantity used
    last_used_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique per organization and item
    UNIQUE(shopping_item_id, organization_id)
);
```

---

## API Design

### RESTful Endpoints Structure

```
/api/v1/
├── auth/
│   ├── POST /login
│   ├── POST /logout
│   ├── POST /refresh
│   └── GET /me
├── organizations/
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   └── DELETE /{id}
├── users/
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   └── DELETE /{id}
├── categories/
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   └── DELETE /{id}
├── supermarkets/
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   └── DELETE /{id}
└── shopping-lists/
    ├── GET /
    ├── POST /
    ├── GET /{id}
    ├── PUT /{id}
    ├── DELETE /{id}
    ├── GET /{id}/items
    ├── POST /{id}/items
    ├── PUT /{id}/items/{item_id}
    ├── DELETE /{id}/items/{item_id}
    ├── GET /{id}/prices
    └── POST /{id}/prices
```

---

## Stage 1: Initial Project Setup

### Objectives
- Establish project structure and development environment
- Configure dependencies and database connection
- Set up testing framework and CI/CD basics
- Create foundation architecture components

### Implementation Steps

#### 1.1 Project Structure
```
restaurant-crm/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection and session
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py            # Base model class
│   │   ├── organization.py
│   │   ├── user.py
│   │   ├── category.py
│   │   └── shopping_list.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── user.py
│   │   └── auth.py
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── base_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependencies (auth, database)
│   │   ├── auth.py            # Authentication routes
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── organizations.py
│   │       └── users.py
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── security.py
├── templates/                 # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── organizations/
│   └── users/
├── static/                    # Static assets
│   ├── css/
│   ├── js/
│   └── img/
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test configuration
│   ├── test_main.py
│   ├── test_auth.py
│   └── fixtures/
├── alembic/                   # Database migrations (Alembic)
│   ├── env.py                 # Alembic environment configuration
│   ├── script.py.mako         # Migration template
│   ├── alembic.ini            # Alembic configuration
│   └── versions/              # Migration scripts
│       └── 001_initial_schema.py
├── .env                       # Environment variables
├── pyproject.toml            # Project configuration and dependencies
├── pytest.ini                # Pytest configuration
└── docker-compose.yml        # Docker services
```

#### 1.2 Dependencies Configuration
Update `pyproject.toml` with required dependencies:

```toml
[project]
name = "restaurant-crm"
version = "0.1.0"
description = "CRM for restaurants"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-multipart>=0.0.6",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "pre-commit>=3.4.0",
    "alembic>=1.12.0",
]
```

#### 1.3 Configuration Management
Create `src/config.py`:

```python
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, Field

class Settings(BaseSettings):
    # Database
    database_url: AnyUrl = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/restaurant_crm")

    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # Application
    app_name: str = Field(default="Restaurant CRM")
    debug: bool = Field(default=True)

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8001"]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

#### 1.4 Database Connection
Create `src/database.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

engine = create_async_engine(settings.database_url, echo=True)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_database() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

#### 1.5 Base Model
Create `src/models/base.py`:

```python
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from .database import Base

class BaseModel(Base):
    __abstract__ = True

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

#### 1.6 Database Migrations with Alembic
Create `alembic/env.py` for async migration support:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import asyncio
from src.database import Base
from src.config import settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set sqlalchemy.url from environment
config.set_main_option("sqlalchemy.url", str(settings.database_url))

# add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = str(settings.database_url)

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

Create `alembic/alembic.ini` configuration:

```ini
[alembic]
sqlalchemy.url = driver://user:password@localhost/dbname
script_location = alembic
sqlalchemy.echo = false
sqlalchemy.echo_pool = false
sqlalchemy.pool_pre_ping = true
sqlalchemy.pool_recycle = 3600

[loggers]
keys = root,sqlalchemy

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

Create initial migration template `alembic/versions/001_initial_schema.py`:

```python
"""Initial schema creation

Revision ID: 001
Revises:
Create Date: 2025-10-30 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create initial database schema."""
    # This will be auto-generated by Alembic
    pass

def downgrade() -> None:
    """Drop initial database schema."""
    pass
```

**Alembic Setup Commands**:
```bash
# Initialize Alembic (already done in project setup)
alembic init alembic

# Create a new migration after model changes
alembic revision --autogenerate -m "Add users table"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current database version
alembic current
```

### Testing Setup
Configure pytest in `pytest.ini`:

```ini
[tool:pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

---

## Stage 2: Client Form Register (CNPJ/CPF Registration System)

### Objectives
- Implement dual registration flows (CNPJ for companies, CPF for individuals)
- Create multi-step registration forms with progressive validation
- Build comprehensive validation for Brazilian IDs (CNPJ/CPF)
- Design mobile-first responsive UI with HTMX integration
- Implement anti-bot protection and external API integration
- Create reusable form components for address and consent management

### Implementation Steps

#### 2.1 Data Models
Create `src/models/client_registration.py`:

```python
from sqlalchemy import Column, String, Text, Date, Boolean, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel

class Address(BaseModel):
    __tablename__ = "addresses"

    cep = Column(String(9), nullable=False)
    endereco = Column(Text, nullable=False)
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))

class RegistrationSession(BaseModel):
    __tablename__ = "registration_sessions"

    session_id = Column(String(255), unique=True, nullable=False)
    registration_type = Column(String(10), nullable=False)  # 'CNPJ' or 'CPF'
    step = Column(Integer, default=1)
    is_completed = Column(Boolean, default=False)
    data = Column(Text)  # JSON string for form data

class CNPJRegistration(BaseModel):
    __tablename__ = "cnpj_registrations"

    qual_seu_negocio = Column(String(100), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False)
    razao_social = Column(String(255), nullable=False)
    seu_nome = Column(String(255), nullable=False)
    sua_funcao = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    celular = Column(String(20), nullable=False)
    terms_accepted = Column(Boolean, default=False)
    marketing_opt_in = Column(Boolean, default=False)

    # Address
    cep = Column(String(9), nullable=False)
    endereco = Column(Text, nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)

    # Relationship
    address = relationship("Address", foreign_keys=[cep, endereco])

class CPFRegistration(BaseModel):
    __tablename__ = "cpf_registrations"

    perfil_compra = Column(String(20), nullable=False)  # 'casa', 'negocio', 'ambos'
    qual_negocio_cpf = Column(String(255))  # Conditional field
    cpf = Column(String(14), unique=True, nullable=False)
    nome_completo = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    genero = Column(String(20), nullable=False)
    celular = Column(String(20), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    terms_accepted = Column(Boolean, default=False)
    marketing_opt_in = Column(Boolean, default=False)

    # Address
    cep = Column(String(9), nullable=False)
    endereco = Column(Text, nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)

    # Relationship
    address = relationship("Address", foreign_keys=[cep, endereco])

# Update User model to include registration data
class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(20), unique=True, index=True, nullable=False)  # CPF or CNPJ
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"))
    role = Column(String(20), nullable=False)  # admin, manager, employee, shopper, customer
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)

    # Registration type
    registration_type = Column(String(10))  # 'CNPJ' or 'CPF'
    registration_data = Column(Text)  # JSON string

    # Relationships
    organization = relationship("Organization", back_populates="users")
```

#### 2.2 Registration Schemas
Create `src/schemas/client_registration.py`:

```python
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import date
import re

# Address schemas
class AddressBase(BaseModel):
    cep: str
    endereco: str
    bairro: str
    cidade: str
    estado: str

class AddressCreate(AddressBase):
    pass

class AddressOut(AddressBase):
    id: str

    class Config:
        from_attributes = True

# CNPJ Registration schemas
class CNPJStep1(BaseModel):
    qual_seu_negocio: str = Field(..., description="Type of business")
    cnpj: str = Field(..., description="Company CNPJ")
    razao_social: str = Field(..., description="Company legal name")
    seu_nome: str = Field(..., description="Your name")
    sua_funcao: str = Field(..., description="Your role in the company")
    email: EmailStr
    celular: str = Field(..., description="Mobile phone")
    terms_accepted: bool = Field(..., description="Terms acceptance")
    marketing_opt_in: Optional[bool] = Field(default=False, description="Marketing consent")

class CNPJStep2(AddressBase):
    recaptcha_token: str = Field(..., description="reCAPTCHA token")

class CNPJRegistrationComplete(CNPJStep1, CNPJStep2):
    pass

class CNPJRegistrationOut(CNPJRegistrationComplete):
    id: str
    created_at: str

    class Config:
        from_attributes = True

# CPF Registration schemas
class CPFStep1(BaseModel):
    perfil_compra: str = Field(..., description="Purchase profile")
    qual_negocio_cpf: Optional[str] = Field(default=None, description="Business name if applicable")
    cpf: str = Field(..., description="Individual CPF")
    nome_completo: str = Field(..., description="Full name")
    email: EmailStr
    genero: str = Field(..., description="Gender")
    celular: str = Field(..., description="Mobile phone")
    terms_accepted: bool = Field(..., description="Terms acceptance")
    marketing_opt_in: Optional[bool] = Field(default=False, description="Marketing consent")

class CPFStep2(BaseModel):
    data_nascimento: date = Field(..., description="Birth date")
    cep: str
    endereco: str
    bairro: str
    cidade: str
    estado: str
    recaptcha_token: str = Field(..., description="reCAPTCHA token")

class CPFRegistrationComplete(CPFStep1, CPFStep2):
    pass

class CPFRegistrationOut(CPFRegistrationComplete):
    id: str
    created_at: str

    class Config:
        from_attributes = True

# Registration session schemas
class RegistrationSessionCreate(BaseModel):
    registration_type: str = Field(..., regex="^(CNPJ|CPF)$")

class RegistrationSessionOut(BaseModel):
    session_id: str
    registration_type: str
    step: int
    is_completed: bool
    data: Optional[Dict[str, Any]] = None
    created_at: str

    class Config:
        from_attributes = True

# Validation utilities
class ValidationUtils:
    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        """Validate CNPJ using official algorithm."""
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj) != 14:
            return False

        # CNPJ validation algorithm
        # Implementation details omitted for brevity
        return True

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Validate CPF using official algorithm."""
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) != 11:
            return False

        # CPF validation algorithm
        # Implementation details omitted for brevity
        return True

    @staticmethod
    def format_cnpj(cnpj: str) -> str:
        """Format CNPJ with proper masking."""
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        return re.sub(r'(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})', r'\1.\2.\3/\4-\5', cnpj)

    @staticmethod
    def format_cpf(cpf: str) -> str:
        """Format CPF with proper masking."""
        cpf = re.sub(r'[^0-9]', '', cpf)
        return re.sub(r'(\d{3})(\d{3})(\d{3})(\d{2})', r'\1.\2.\3-\4', cpf)

    @staticmethod
    def format_phone(phone: str) -> str:
        """Format Brazilian phone number."""
        phone = re.sub(r'[^0-9]', '', phone)
        if len(phone) == 11:
            return re.sub(r'(\d{2})(\d{5})(\d{4})', r'(\1) \2-\3', phone)
        elif len(phone) == 10:
            return re.sub(r'(\d{2})(\d{4})(\d{4})', r'(\1) \2-\3', phone)
        return phone
```

#### 2.3 Registration Service
Create `src/services/client_registration_service.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, Dict, Any
import json
import uuid
from ..models.client_registration import (
    RegistrationSession, CNPJRegistration, CPFRegistration, Address
)
from ..schemas.client_registration import (
    RegistrationSessionCreate, RegistrationSessionOut,
    CNPJRegistrationComplete, CNPJRegistrationOut,
    CPFRegistrationComplete, CPFRegistrationOut,
    ValidationUtils
)
from .base_service import BaseService

class ClientRegistrationService:
    def __init__(self):
        self.session_service = BaseService(RegistrationSession)
        self.cnpj_service = BaseService(CNPJRegistration)
        self.cpf_service = BaseService(CPFRegistration)
        self.address_service = BaseService(Address)

    async def create_registration_session(
        self,
        db: AsyncSession,
        registration_type: str
    ) -> RegistrationSession:
        """Create a new registration session."""
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "registration_type": registration_type,
            "step": 1,
            "is_completed": False,
            "data": None
        }

        session = await self.session_service.create(db, session_data)
        return session

    async def get_session(
        self,
        db: AsyncSession,
        session_id: str
    ) -> Optional[RegistrationSession]:
        """Get registration session by ID."""
        return await self.session_service.get_by_field(db, "session_id", session_id)

    async def update_session_data(
        self,
        db: AsyncSession,
        session_id: str,
        step: int,
        data: Dict[str, Any]
    ) -> RegistrationSession:
        """Update session with form data."""
        session = await self.get_session(db, session_id)
        if not session:
            raise ValueError("Registration session not found")

        update_data = {
            "step": step,
            "data": json.dumps(data)
        }

        return await self.session_service.update(db, session.id, update_data)

    async def complete_cnpj_registration(
        self,
        db: AsyncSession,
        registration_data: CNPJRegistrationComplete
    ) -> CNPJRegistration:
        """Complete CNPJ registration."""
        # Validate CNPJ
        if not ValidationUtils.validate_cnpj(registration_data.cnpj):
            raise ValueError("Invalid CNPJ")

        # Check for existing CNPJ
        existing = await self.cnpj_service.get_by_field(db, "cnpj", registration_data.cnpj)
        if existing:
            raise ValueError("CNPJ já cadastrado")

        # Create address
        address_data = {
            "cep": registration_data.cep,
            "endereco": registration_data.endereco,
            "bairro": registration_data.bairro,
            "cidade": registration_data.cidade,
            "estado": registration_data.estado
        }
        address = await self.address_service.create(db, address_data)

        # Create CNPJ registration
        registration_dict = registration_data.dict()
        registration_dict.pop("recaptcha_token")  # Don't store reCAPTCHA token

        return await self.cnpj_service.create(db, registration_dict)

    async def complete_cpf_registration(
        self,
        db: AsyncSession,
        registration_data: CPFRegistrationComplete
    ) -> CPFRegistration:
        """Complete CPF registration."""
        # Validate CPF
        if not ValidationUtils.validate_cpf(registration_data.cpf):
            raise ValueError("Invalid CPF")

        # Check for existing CPF
        existing = await self.cpf_service.get_by_field(db, "cpf", registration_data.cpf)
        if existing:
            raise ValueError("CPF já cadastrado")

        # Create address
        address_data = {
            "cep": registration_data.cep,
            "endereco": registration_data.endereco,
            "bairro": registration_data.bairro,
            "cidade": registration_data.cidade,
            "estado": registration_data.estado
        }
        address = await self.address_service.create(db, address_data)

        # Create CPF registration
        registration_dict = registration_data.dict()
        registration_dict.pop("recaptcha_token")  # Don't store reCAPTCHA token

        return await self.cpf_service.create(db, registration_dict)

    async def validate_document_uniqueness(
        self,
        db: AsyncSession,
        document: str,
        document_type: str
    ) -> Dict[str, Any]:
        """Validate document uniqueness with real-time feedback."""
        if document_type == "CNPJ":
            existing = await self.cnpj_service.get_by_field(db, "cnpj", document)
            return {
                "valid": not existing,
                "message": "CNPJ já cadastrado" if existing else "CNPJ available"
            }
        elif document_type == "CPF":
            existing = await self.cpf_service.get_by_field(db, "cpf", document)
            return {
                "valid": not existing,
                "message": "CPF já cadastrado" if existing else "CPF available"
            }
        return {"valid": False, "message": "Invalid document type"}

class ViaCEPService:
    """Service for ViaCEP API integration."""

    @staticmethod
    async def get_address_by_cep(cep: str) -> Optional[Dict[str, str]]:
        """Get address information from ViaCEP API."""
        import httpx

        cep = re.sub(r'[^0-9]', '', cep)
        if len(cep) != 8:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("erro"):
                        return None
                    return {
                        "endereco": data.get("logradouro", ""),
                        "bairro": data.get("bairro", ""),
                        "cidade": data.get("localidade", ""),
                        "estado": data.get("uf", "")
                    }
        except Exception:
            return None

        return None
```

#### 2.4 Registration API Routes
Create `src/api/v1/registration.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from ...database import get_database
from ...schemas.client_registration import (
    RegistrationSessionCreate, RegistrationSessionOut,
    CNPJStep1, CNPJStep2, CNPJRegistrationOut,
    CPFStep1, CPFStep2, CPFRegistrationOut,
    ValidationUtils
)
from ...services.client_registration_service import ClientRegistrationService, ViaCEPService

router = APIRouter(prefix="/registration", tags=["registration"])

@router.post("/session", response_model=RegistrationSessionOut)
async def create_registration_session(
    session_data: RegistrationSessionCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new registration session."""
    service = ClientRegistrationService()
    session = await service.create_registration_session(db, session_data.registration_type)
    return session

@router.get("/session/{session_id}", response_model=RegistrationSessionOut)
async def get_registration_session(
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get registration session details."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Registration session not found")
    return session

# CNPJ Registration Endpoints
@router.post("/cnpj/step1")
async def validate_cnpj_step1(
    session_id: str,
    step1_data: CNPJStep1,
    db: AsyncSession = Depends(get_database)
):
    """Validate CNPJ step 1 data and store in session."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)

    if not session or session.registration_type != "CNPJ":
        raise HTTPException(status_code=404, detail="Invalid registration session")

    # Validate CNPJ format
    if not ValidationUtils.validate_cnpj(step1_data.cnpj):
        raise HTTPException(status_code=400, detail="Invalid CNPJ format")

    # Check uniqueness
    uniqueness_check = await service.validate_document_uniqueness(
        db, step1_data.cnpj, "CNPJ"
    )
    if not uniqueness_check["valid"]:
        raise HTTPException(status_code=400, detail=uniqueness_check["message"])

    # Store step 1 data
    await service.update_session_data(db, session_id, 1, step1_data.dict())

    return {"message": "Step 1 validation successful", "next_step": 2}

@router.post("/cnpj/step2")
async def complete_cnpj_registration(
    session_id: str,
    step2_data: CNPJStep2,
    db: AsyncSession = Depends(get_database)
):
    """Complete CNPJ registration."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)

    if not session or session.registration_type != "CNPJ":
        raise HTTPException(status_code=404, detail="Invalid registration session")

    # Verify reCAPTCHA (implement with actual reCAPTCHA service)
    # if not await verify_recaptcha(step2_data.recaptcha_token):
    #     raise HTTPException(status_code=400, detail="reCAPTCHA verification failed")

    # Get stored step 1 data
    if session.data:
        step1_data = CNPJStep1(**json.loads(session.data))
        complete_data = {**step1_data.dict(), **step2_data.dict()}
        registration = await service.complete_cnpj_registration(db, CNPJRegistrationComplete(**complete_data))

        # Mark session as completed
        await service.update_session_data(db, session_id, 2, {"completed": True})

        return {"message": "Registration completed successfully", "registration_id": registration.id}

    raise HTTPException(status_code=400, detail="Step 1 data not found")

# CPF Registration Endpoints
@router.post("/cpf/step1")
async def validate_cpf_step1(
    session_id: str,
    step1_data: CPFStep1,
    db: AsyncSession = Depends(get_database)
):
    """Validate CPF step 1 data and store in session."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)

    if not session or session.registration_type != "CPF":
        raise HTTPException(status_code=404, detail="Invalid registration session")

    # Validate CPF format
    if not ValidationUtils.validate_cpf(step1_data.cpf):
        raise HTTPException(status_code=400, detail="Invalid CPF format")

    # Check uniqueness
    uniqueness_check = await service.validate_document_uniqueness(
        db, step1_data.cpf, "CPF"
    )
    if not uniqueness_check["valid"]:
        raise HTTPException(status_code=400, detail=uniqueness_check["message"])

    # Store step 1 data
    await service.update_session_data(db, session_id, 1, step1_data.dict())

    return {"message": "Step 1 validation successful", "next_step": 2}

@router.post("/cpf/step2")
async def complete_cpf_registration(
    session_id: str,
    step2_data: CPFStep2,
    db: AsyncSession = Depends(get_database)
):
    """Complete CPF registration."""
    service = ClientRegistrationService()
    session = await service.get_session(db, session_id)

    if not session or session.registration_type != "CPF":
        raise HTTPException(status_code=404, detail="Invalid registration session")

    # Verify reCAPTCHA (implement with actual reCAPTCHA service)
    # if not await verify_recaptcha(step2_data.recaptcha_token):
    #     raise HTTPException(status_code=400, detail="reCAPTCHA verification failed")

    # Get stored step 1 data
    if session.data:
        step1_data = CPFStep1(**json.loads(session.data))
        complete_data = {**step1_data.dict(), **step2_data.dict()}
        registration = await service.complete_cpf_registration(db, CPFRegistrationComplete(**complete_data))

        # Mark session as completed
        await service.update_session_data(db, session_id, 2, {"completed": True})

        return {"message": "Registration completed successfully", "registration_id": registration.id}

    raise HTTPException(status_code=400, detail="Step 1 data not found")

# Utility Endpoints
@router.get("/validate/document/{document_type}/{document}")
async def validate_document_uniqueness(
    document_type: str,
    document: str,
    db: AsyncSession = Depends(get_database)
):
    """Validate document uniqueness in real-time."""
    service = ClientRegistrationService()
    return await service.validate_document_uniqueness(db, document, document_type)

@router.get("/address/cep/{cep}")
async def get_address_by_cep(cep: str):
    """Get address information by CEP."""
    address = await ViaCEPService.get_address_by_cep(cep)
    if not address:
        raise HTTPException(status_code=404, detail="CEP not found")
    return address
```

#### 2.5 Mobile-First Registration Templates
Create comprehensive registration templates in `templates/registration/`:

**Registration Type Selection**: `templates/registration/select-type.html`
```html
{% extends "base.html" %}

{% block title %}Choose Registration Type - CompraJá!{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
        <div>
            <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                Choose Registration Type
            </h2>
            <p class="mt-2 text-center text-sm text-gray-600">
                Select how you want to register on CompraJá!
            </p>
        </div>

        <div class="space-y-4">
            <!-- CNPJ Option -->
            <button hx-post="/registration/session"
                    hx-vals='{"registration_type": "CNPJ"}'
                    hx-target="#result"
                    hx-swap="innerHTML"
                    class="w-full flex flex-col items-center p-6 border-2 border-gray-300 rounded-lg hover:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                <div class="text-4xl mb-2">🏢</div>
                <h3 class="text-lg font-medium text-gray-900">Company Registration</h3>
                <p class="text-sm text-gray-500 text-center mt-1">Register your restaurant or business with CNPJ</p>
            </button>

