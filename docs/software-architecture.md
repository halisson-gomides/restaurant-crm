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
            raise ValueError("CNPJ already registered")
        
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
            raise ValueError("CPF already registered")
        
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
                "message": "CNPJ already registered" if existing else "CNPJ available"
            }
        elif document_type == "CPF":
            existing = await self.cpf_service.get_by_field(db, "cpf", document)
            return {
                "valid": not existing,
                "message": "CPF already registered" if existing else "CPF available"
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
            
            <!-- CPF Option -->
            <button hx-post="/registration/session" 
                    hx-vals='{"registration_type": "CPF"}'
                    hx-target="#result" 
                    hx-swap="innerHTML"
                    class="w-full flex flex-col items-center p-6 border-2 border-gray-300 rounded-lg hover:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                <div class="text-4xl mb-2">👤</div>
                <h3 class="text-lg font-medium text-gray-900">Personal Registration</h3>
                <p class="text-sm text-gray-500 text-center mt-1">Register as an individual with CPF</p>
            </button>
        </div>
        
        <div id="result" class="text-center"></div>
    </div>
</div>

<!-- Loading indicator -->
<div id="loading" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
    <div class="bg-white rounded-lg p-6">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-2 text-sm text-gray-600">Processing...</p>
    </div>
</div>

<script>
document.addEventListener('htmx:beforeRequest', function(e) {
    if (e.detail.elt.tagName === 'BUTTON') {
        document.getElementById('loading').classList.remove('hidden');
    }
});

document.addEventListener('htmx:afterRequest', function(e) {
    document.getElementById('loading').classList.add('hidden');
});
</script>
{% endblock %}
```

**CNPJ Step 1**: `templates/registration/cnpj-step1.html`
```html
{% extends "base.html" %}

{% block title %}Company Registration - Step 1 - CompraJá!{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Progress Indicator -->
    <div class="mb-8">
        <nav aria-label="Progress">
            <ol class="flex items-center">
                <li class="relative flex-1 after:content-[''] after:absolute after:top-4 after:w-full after:h-0.5 after:bg-indigo-600 after:-right-1/2">
                    <div class="relative w-8 h-8 flex items-center justify-center bg-indigo-600 text-white text-sm font-medium rounded-full">1</div>
                    <span class="absolute top-10 left-0 text-sm text-indigo-600 font-medium">Business Info</span>
                </li>
                <li class="relative flex-1">
                    <div class="relative w-8 h-8 flex items-center justify-center bg-gray-300 text-gray-500 text-sm font-medium rounded-full">2</div>
                    <span class="absolute top-10 left-0 text-sm text-gray-500">Address</span>
                </li>
            </ol>
        </nav>
    </div>

    <div class="bg-white shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
            <h1 class="text-2xl font-bold text-gray-900 mb-6">Business Information</h1>
            
            <form hx-post="/registration/cnpj/step1" 
                  hx-vals='{"session_id": "{{ session_id }}"}'
                  hx-target="#result" 
                  hx-swap="innerHTML"
                  class="space-y-6">
                
                <!-- Business Type -->
                <div>
                    <label for="qual_seu_negocio" class="block text-sm font-medium text-gray-700">What is your business? *</label>
                    <select id="qual_seu_negocio" name="qual_seu_negocio" required
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                        <option value="">Select business type</option>
                        <option value="Academia">Academia</option>
                        <option value="Adega">Adega</option>
                        <option value="Bar">Bar</option>
                        <option value="Bomboniere">Bomboniere</option>
                        <option value="Cantina">Cantina</option>
                        <option value="Clube esportivo">Clube esportivo</option>
                        <option value="Condomínio">Condomínio</option>
                        <option value="Confeitaria">Confeitaria</option>
                        <option value="Doceria">Doceria</option>
                        <option value="Dogueiro">Dogueiro</option>
                        <option value="Escola">Escola</option>
                        <option value="Food service">Food service</option>
                        <option value="Hotel">Hotel</option>
                        <option value="Instituição religiosa">Instituição religiosa</option>
                        <option value="Lanchonete">Lanchonete</option>
                        <option value="Mercearia">Mercearia</option>
                        <option value="Mini mercado">Mini mercado</option>
                        <option value="Padaria">Padaria</option>
                        <option value="Pastelaria">Pastelaria</option>
                        <option value="Pizzaria">Pizzaria</option>
                        <option value="Restaurante">Restaurante</option>
                        <option value="Outros">Outros</option>
                    </select>
                </div>
                
                <!-- CNPJ -->
                <div>
                    <label for="cnpj" class="block text-sm font-medium text-gray-700">CNPJ *</label>
                    <input type="text" 
                           id="cnpj" 
                           name="cnpj" 
                           required 
                           placeholder="00.000.000/0000-00"
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                           hx-get="/registration/validate/document/CNPJ"
                           hx-trigger="blur"
                           hx-target="#cnpj-error"
                           hx-swap="innerHTML">
                    <div id="cnpj-error" class="mt-1 text-sm text-red-600"></div>
                </div>
                
                <!-- Company Name -->
                <div>
                    <label for="razao_social" class="block text-sm font-medium text-gray-700">Company Legal Name *</label>
                    <input type="text" 
                           id="razao_social" 
                           name="razao_social" 
                           required
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                </div>
                
                <!-- Your Name -->
                <div>
                    <label for="seu_nome" class="block text-sm font-medium text-gray-700">Your Name *</label>
                    <input type="text" 
                           id="seu_nome" 
                           name="seu_nome" 
                           required
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                </div>
                
                <!-- Your Role -->
                <div>
                    <label for="sua_funcao" class="block text-sm font-medium text-gray-700">Your Role in the Company *</label>
                    <select id="sua_funcao" name="sua_funcao" required
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                        <option value="">Select your role</option>
                        <option value="Proprietário">Proprietário</option>
                        <option value="Gerente">Gerente</option>
                        <option value="Estoquista">Estoquista</option>
                    </select>
                </div>
                
                <!-- Email -->
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">Email *</label>
                    <input type="email" 
                           id="email" 
                           name="email" 
                           required
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                </div>
                
                <!-- Mobile -->
                <div>
                    <label for="celular" class="block text-sm font-medium text-gray-700">Mobile Phone *</label>
                    <input type="tel" 
                           id="celular" 
                           name="celular" 
                           required
                           placeholder="(11) 99999-9999"
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                </div>
                
                <!-- Terms and Marketing -->
                <div class="space-y-4">
                    <div class="flex items-start">
                        <input id="terms_accepted" 
                               name="terms_accepted" 
                               type="checkbox" 
                               required
                               class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded mt-1">
                        <label for="terms_accepted" class="ml-3 block text-sm text-gray-700">
                            I agree to the <a href="#" class="text-indigo-600 hover:text-indigo-500">Privacy Policy</a> *
                        </label>
                    </div>
                    
                    <div class="flex items-start">
                        <input id="marketing_opt_in" 
                               name="marketing_opt_in" 
                               type="checkbox"
                               class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded mt-1">
                        <label for="marketing_opt_in" class="ml-3 block text-sm text-gray-700">
                            I want to receive emails with promotions and material from CompraJá! and its partners
                        </label>
                    </div>
                </div>
                
                <!-- Navigation -->
                <div class="flex justify-between pt-6">
                    <a href="/registration/select-type" 
                       class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                        Back
                    </a>
                    <button type="submit" 
                            class="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Continue to Address
                    </button>
                </div>
            </form>
            
            <div id="result" class="mt-4"></div>
        </div>
    </div>
</div>

<script>
// CNPJ formatting
document.getElementById('cnpj').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    let formatted = value.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    e.target.value = formatted;
});

// Mobile formatting
document.getElementById('celular').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length <= 11) {
        value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    }
    e.target.value = value;
});
</script>
{% endblock %}
```

**Reusable Address Component**: `templates/components/address-form.html`
```html
<!-- Reusable Address Form Component -->
<div class="space-y-4">
    <div>
        <label for="cep" class="block text-sm font-medium text-gray-700">CEP *</label>
        <input type="text" 
               id="cep" 
               name="cep" 
               required
               placeholder="00000-000"
               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
               hx-get="/registration/address/cep"
               hx-trigger="blur"
               hx-target="#address-fields"
               hx-swap="innerHTML">
    </div>
    
    <div id="address-fields" class="space-y-4">
        <div>
            <label for="endereco" class="block text-sm font-medium text-gray-700">Address *</label>
            <input type="text" 
                   id="endereco" 
                   name="endereco" 
                   required
                   class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
        </div>
        
        <div>
            <label for="bairro" class="block text-sm font-medium text-gray-700">Neighborhood *</label>
            <input type="text" 
                   id="bairro" 
                   name="bairro" 
                   required
                   class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
        </div>
        
        <div>
            <label for="cidade" class="block text-sm font-medium text-gray-700">City *</label>
            <input type="text" 
                   id="cidade" 
                   name="cidade" 
                   required
                   class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
        </div>
        
        <div>
            <label for="estado" class="block text-sm font-medium text-gray-700">State *</label>
            <select id="estado" name="estado" required
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                <option value="">Select state</option>
                <option value="AC">Acre</option>
                <option value="AL">Alagoas</option>
                <option value="AP">Amapá</option>
                <option value="AM">Amazonas</option>
                <option value="BA">Bahia</option>
                <option value="CE">Ceará</option>
                <option value="DF">Distrito Federal</option>
                <option value="ES">Espírito Santo</option>
                <option value="GO">Goiás</option>
                <option value="MA">Maranhão</option>
                <option value="MT">Mato Grosso</option>
                <option value="MS">Mato Grosso do Sul</option>
                <option value="MG">Minas Gerais</option>
                <option value="PA">Pará</option>
                <option value="PB">Paraíba</option>
                <option value="PR">Paraná</option>
                <option value="PE">Pernambuco</option>
                <option value="PI">Piauí</option>
                <option value="RJ">Rio de Janeiro</option>
                <option value="RN">Rio Grande do Norte</option>
                <option value="RS">Rio Grande do Sul</option>
                <option value="RO">Rondônia</option>
                <option value="RR">Roraima</option>
                <option value="SC">Santa Catarina</option>
                <option value="SP">São Paulo</option>
                <option value="SE">Sergipe</option>
                <option value="TO">Tocantins</option>
            </select>
        </div>
    </div>
</div>

<script>
// CEP formatting
document.getElementById('cep').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length <= 8) {
        value = value.replace(/(\d{5})(\d{3})/, '$1-$2');
    }
    e.target.value = value;
});
</script>
```

This comprehensive Stage 2 implementation provides:
1. **Dual Registration Flows**: Separate CNPJ and CPF registration processes
2. **Multi-step Forms**: Progressive validation with step indicators
3. **Mobile-First Design**: Responsive UI optimized for mobile devices
4. **HTMX Integration**: Dynamic form validation and progress
5. **External API Integration**: ViaCEP for address auto-fill
6. **Anti-bot Protection**: reCAPTCHA integration framework
7. **Reusable Components**: Address form and consent blocks
8. **Comprehensive Validation**: CPF/CNPJ validation and uniqueness checks
9. **Professional UI**: Clean, accessible design with proper UX patterns

---

## Stage 3: Authentication System

### Objectives
- Implement role-based authentication system
- Create user profile management with CPF/CNPJ support
- Build secure session management
- Design protected routes and middleware

### Implementation Steps

#### 3.1 User Models
Create `src/models/user.py`:

```python
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"))
    role = Column(String(20), nullable=False)  # admin, manager, employee, shopper, customer
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")

class UserRole(BaseModel):
    __tablename__ = "user_roles"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    
    user = relationship("User", back_populates="user_roles")
    organization = relationship("Organization", back_populates="user_roles")
```

Update `src/models/organization.py` to include relationships:

```python
from sqlalchemy import Column, String, Text, DateTime, func, orm
from .base import BaseModel

class Organization(BaseModel):
    __tablename__ = "organizations"
    
    cnpj = Column(String(18), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    trade_name = Column(String(255))
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255), unique=True, index=True)
    
    # Relationships
    users = orm.relationship("User", back_populates="organization", cascade="all, delete-orphan")
    user_roles = orm.relationship("UserRole", back_populates="organization")
```

#### 3.2 Authentication Schemas
Create `src/schemas/auth.py`:

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import re

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    username: str
    password: str
    organization_id: str
    role: str
    
    @validator('username')
    def validate_username(cls, v):
        # CPF: 11 digits, CNPJ: 14 digits
        username = re.sub(r'[^0-9]', '', v)
        if len(username) not in [11, 14]:
            raise ValueError('Username must be CPF (11 digits) or CNPJ (14 digits)')
        return username
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['admin', 'manager', 'employee', 'shopper', 'customer']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(UserBase):
    id: str
    username: str
    organization_id: str
    role: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
```

#### 3.3 Security Utilities
Create `src/utils/security.py`:

```python
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None
```

#### 3.4 Authentication Service
Create `src/services/auth_service.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User
from ..schemas.auth import UserCreate, UserLogin, UserOut, Token
from ..utils.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from ..config import settings

class AuthService:
    async def register_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if user already exists
        result = await db.execute(select(User).where(User.username == user_data.username))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError("Username already registered")
        
        # Check email uniqueness
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_email = result.scalar_one_or_none()
        if existing_email:
            raise ValueError("Email already registered")
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            organization_id=user_data.organization_id,
            role=user_data.role,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    async def authenticate_user(self, db: AsyncSession, user_data: UserLogin) -> Optional[User]:
        """Authenticate user with username and password."""
        result = await db.execute(select(User).where(User.username == user_data.username))
        user = result.scalar_one_or_none()
        if not user or not verify_password(user_data.password, user.hashed_password):
            return None
        return user
    
    async def create_access_token(self, user: User) -> Token:
        """Create access token for user."""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
```

#### 3.5 Authentication Dependencies
Create `src/api/deps.py`:

```python
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_database
from ..utils.security import verify_token
from ..models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
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
```

#### 3.6 Authentication API Routes
Create `src/api/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_database
from ..schemas.auth import UserCreate, UserLogin, UserOut, Token
from ..services.auth_service import AuthService
from ..utils.security import verify_token
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_database)
):
    """Register a new user."""
    auth_service = AuthService()
    try:
        user = await auth_service.register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_database)
):
    """Authenticate user and return access token."""
    auth_service = AuthService()
    user = await auth_service.authenticate_user(db, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    token = await auth_service.create_access_token(user)
    return token

@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)."""
    return {"message": "Successfully logged out"}
```

#### 3.7 Login Template
Create `templates/auth/login.html`:

```html
{% extends "base.html" %}

{% block title %}Login - Restaurant CRM{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
        <div>
            <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                Sign in to Restaurant CRM
            </h2>
            <p class="mt-2 text-center text-sm text-gray-600">
                Enter your CPF/CNPJ and password to access your account
            </p>
        </div>
        
        <form hx-post="/auth/login" hx-target="#error" hx-swap="innerHTML" 
              class="mt-8 space-y-6">
            <div>
                <label for="username" class="sr-only">CPF/CNPJ</label>
                <input 
                    id="username" 
                    name="username" 
                    type="text" 
                    required 
                    class="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="CPF (11 digits) or CNPJ (14 digits)"
                    hx-post="/auth/validate-username" 
                    hx-trigger="blur"
                >
            </div>
            
            <div>
                <label for="password" class="sr-only">Password</label>
                <input 
                    id="password" 
                    name="password" 
                    type="password" 
                    required 
                    class="relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                    placeholder="Password"
                >
            </div>
            
            <div>
                <button 
                    type="submit" 
                    class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                    Sign in
                </button>
            </div>
            
            <div id="error" class="text-red-600 text-center"></div>
        </form>
    </div>
</div>

<script>
// Username formatting
document.getElementById('username').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length <= 11) {
        // CPF format: 000.000.000-00
        value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    } else if (value.length <= 14) {
        // CNPJ format: 00.000.000/0000-00
        value = value.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    e.target.value = value;
});
</script>
{% endblock %}
```

---

## Stage 4: Restaurant Shopping List

### Objectives
- Build category management system
- Create shopping list CRUD operations
- Implement shopper interface with price tracking
- **Design mobile-responsive UI for field use**
  - **Mobile-first responsive design (320px+ screens)**
  - **Touch-optimized interface with 44px+ touch targets**
  - **Fast loading and smooth interactions on mobile devices**
  - **Offline-capable with HTMX's enhanced local storage**

### Implementation Steps

#### 4.1 Category Models
Create `src/models/category.py`:

```python
from sqlalchemy import Column, String, Text, Integer, Boolean, orm
from .base import BaseModel

class Category(BaseModel):
    __tablename__ = "categories"
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    shopping_list_items = orm.relationship("ShoppingListItem", back_populates="category")

class Supermarket(BaseModel):
    __tablename__ = "supermarkets"
    
    name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    item_prices = orm.relationship("ItemPrice", back_populates="supermarkets")

class ShoppingList(BaseModel):
    __tablename__ = "shopping_lists"
    
    organization_id = Column(String, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(20), default="draft")  # draft, active, completed
    created_by = Column(String)
    
    # Relationships
    items = orm.relationship("ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan")

class ShoppingListItem(BaseModel):
    __tablename__ = "shopping_list_items"
    
    shopping_list_id = Column(String, nullable=False)
    category_id = Column(String, nullable=False)
    name = Column(String(255), nullable=False)
    quantity = Column(Integer)
    unit = Column(String(20))
    estimated_price = Column(Integer)  # Stored in cents
    notes = Column(Text)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    shopping_list = orm.relationship("ShoppingList", back_populates="items")
    category = orm.relationship("Category", back_populates="shopping_list_items")
    item_prices = orm.relationship("ItemPrice", back_populates="shopping_list_item", cascade="all, delete-orphan")

class ItemPrice(BaseModel):
    __tablename__ = "item_prices"
    
    shopping_list_item_id = Column(String, nullable=False)
    supermarket_id = Column(String, nullable=False)
    price = Column(Integer, nullable=False)  # Stored in cents
    checked_by = Column(String)
    
    # Relationships
    shopping_list_item = orm.relationship("ShoppingListItem", back_populates="item_prices")
    supermarkets = orm.relationship("Supermarket", back_populates="item_prices")
```

#### 4.2 Shopping List Schemas
Create `src/schemas/shopping_list.py`:

```python
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    sort_order: Optional[int] = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True

class SupermarketBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None

class SupermarketCreate(SupermarketBase):
    pass

class SupermarketOut(SupermarketBase):
    id: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True

class ShoppingListItemBase(BaseModel):
    name: str
    category_id: str
    quantity: Optional[int] = None
    unit: Optional[str] = None
    estimated_price: Optional[float] = None
    notes: Optional[str] = None

class ShoppingListItemCreate(ShoppingListItemBase):
    pass

class ShoppingListItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    estimated_price: Optional[float] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = None

class ShoppingListItemOut(ShoppingListItemBase):
    id: str
    is_completed: bool
    category: CategoryOut
    created_at: str
    
    class Config:
        from_attributes = True

class ShoppingListBase(BaseModel):
    name: str
    organization_id: str

class ShoppingListCreate(ShoppingListBase):
    pass

class ShoppingListOut(ShoppingListBase):
    id: str
    status: str
    created_by: str
    items: List[ShoppingListItemOut] = []
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class ItemPriceBase(BaseModel):
    shopping_list_item_id: str
    supermarket_id: str
    price: float

class ItemPriceCreate(ItemPriceBase):
    pass

class ItemPriceOut(ItemPriceBase):
    id: str
    checked_by: str
    checked_at: str
    supermarkets: SupermarketOut
    
    class Config:
        from_attributes = True

# Helper models for UI
class CategoryWithItems(CategoryOut):
    items: List[ShoppingListItemOut] = []
    completed_count: int = 0
    total_count: int = 0

class ShoppingListDetailOut(ShoppingListOut):
    categories: List[CategoryWithItems] = []
```

#### 4.3 Shopping List Service
Create `src/services/shopping_list_service.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from ..models.shopping_list import ShoppingList, ShoppingListItem, Category, ItemPrice
from ..schemas.shopping_list import (
    ShoppingListCreate, ShoppingListOut, ShoppingListDetailOut,
    CategoryCreate, CategoryOut, SupermarketCreate, SupermarketOut,
    ShoppingListItemCreate, ShoppingListItemOut, ItemPriceCreate, ItemPriceOut
)
from .base_service import BaseService

class CategoryService(BaseService):
    def __init__(self):
        super().__init__(Category)
    
    async def create_category(self, db: AsyncSession, category_data: CategoryCreate) -> Category:
        return await self.create(db, category_data.dict())
    
    async def list_active_categories(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
        return await self.list(db, skip=skip, limit=limit, filters={"is_active": True})

class ShoppingListService(BaseService):
    def __init__(self):
        super().__init__(ShoppingList)
    
    async def create_shopping_list(self, db: AsyncSession, list_data: ShoppingListCreate, user_id: str) -> ShoppingList:
        data = list_data.dict()
        data["created_by"] = user_id
        return await self.create(db, data)
    
    async def get_shopping_list_detail(self, db: AsyncSession, list_id: str) -> Optional[ShoppingListDetailOut]:
        """Get shopping list with items organized by category."""
        result = await db.execute(
            select(ShoppingList)
            .options(
                selectinload(ShoppingList.items).selectinload(ShoppingListItem.category)
            )
            .where(ShoppingList.id == list_id)
        )
        
        shopping_list = result.scalar_one_or_none()
        if not shopping_list:
            return None
        
        # Organize items by category
        category_items = {}
        for item in shopping_list.items:
            category_id = item.category_id
            if category_id not in category_items:
                category_items[category_id] = []
            category_items[category_id].append(item)
        
        # Build categories with items
        categories = []
        for category_id, items in category_items.items():
            if items:
                category = items[0].category
                category_with_items = {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "sort_order": category.sort_order,
                    "is_active": category.is_active,
                    "created_at": category.created_at.isoformat(),
                    "items": [ShoppingListItemOut.from_orm(item) for item in items],
                    "completed_count": sum(1 for item in items if item.is_completed),
                    "total_count": len(items)
                }
                categories.append(category_with_items)
        
        return ShoppingListDetailOut(
            id=shopping_list.id,
            name=shopping_list.name,
            organization_id=shopping_list.organization_id,
            status=shopping_list.status,
            created_by=shopping_list.created_by,
            items=[],
            categories=categories,
            created_at=shopping_list.created_at.isoformat(),
            updated_at=shopping_list.updated_at.isoformat()
        )
    
    async def add_item_to_list(self, db: AsyncSession, list_id: str, item_data: ShoppingListItemCreate) -> ShoppingListItem:
        service = BaseService(ShoppingListItem)
        data = item_data.dict()
        data["shopping_list_id"] = list_id
        return await service.create(db, data)
    
    async def toggle_item_completion(self, db: AsyncSession, item_id: str) -> ShoppingListItem:
        service = BaseService(ShoppingListItem)
        item = await service.get_by_id(db, item_id)
        if item:
            item.is_completed = not item.is_completed
            await db.commit()
            await db.refresh(item)
        return item

class ItemPriceService(BaseService):
    def __init__(self):
        super().__init__(ItemPrice)
    
    async def add_item_price(self, db: AsyncSession, price_data: ItemPriceCreate, user_id: str) -> ItemPrice:
        data = price_data.dict()
        data["checked_by"] = user_id
        data["price"] = int(data["price"] * 100)  # Convert to cents
        return await self.create(db, data)
    
    async def get_item_prices(self, db: AsyncSession, item_id: str) -> list[ItemPrice]:
        return await self.list(db, filters={"shopping_list_item_id": item_id})
```

#### 4.4 Shopping List API Routes
Create `src/api/v1/shopping_lists.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...database import get_database
from ...schemas.shopping_list import (
    ShoppingListCreate, ShoppingListOut, ShoppingListDetailOut,
    CategoryCreate, CategoryOut, SupermarketCreate, SupermarketOut,
    ShoppingListItemCreate, ItemPriceCreate
)
from ...services.shopping_list_service import CategoryService, ShoppingListService, ItemPriceService
from ...api.deps import get_current_user

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])

# Categories
@router.post("/categories", response_model=CategoryOut)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Create a new category."""
    service = CategoryService()
    return await service.create_category(db, category_data)

@router.get("/categories", response_model=List[CategoryOut])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database)
):
    """List all active categories."""
    service = CategoryService()
    return await service.list_active_categories(db, skip=skip, limit=limit)

# Supermarkets
@router.post("/supermarkets", response_model=SupermarketOut)
async def create_supermarket(
    supermarket_data: SupermarketCreate,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Create a new supermarket."""
    service = ItemPriceService()  # Will need separate supermarket service
    # Implementation similar to categories
    pass

# Shopping Lists
@router.post("/", response_model=ShoppingListOut)
async def create_shopping_list(
    list_data: ShoppingListCreate,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Create a new shopping list."""
    service = ShoppingListService()
    return await service.create_shopping_list(db, list_data, current_user.id)

@router.get("/", response_model=List[ShoppingListOut])
async def list_shopping_lists(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """List shopping lists for user's organization."""
    service = ShoppingListService()
    return await service.list(db, skip=skip, limit=limit, 
                             filters={"organization_id": current_user.organization_id})

@router.get("/{list_id}", response_model=ShoppingListDetailOut)
async def get_shopping_list_detail(
    list_id: str,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get shopping list detail with items organized by category."""
    service = ShoppingListService()
    shopping_list = await service.get_shopping_list_detail(db, list_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return shopping_list

@router.post("/{list_id}/items", response_model=dict)
async def add_item_to_list(
    list_id: str,
    item_data: ShoppingListItemCreate,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Add item to shopping list."""
    service = ShoppingListService()
    item = await service.add_item_to_list(db, list_id, item_data)
    return {"message": "Item added successfully", "item_id": item.id}

@router.put("/{list_id}/items/{item_id}/toggle")
async def toggle_item_completion(
    list_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Toggle item completion status."""
    service = ShoppingListService()
    item = await service.toggle_item_completion(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item updated", "is_completed": item.is_completed}

# Price Tracking
@router.post("/prices")
async def add_item_price(
    price_data: ItemPriceCreate,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Add price for an item at a supermarket."""
    service = ItemPriceService()
    price = await service.add_item_price(db, price_data, current_user.id)
    return {"message": "Price added successfully", "price_id": price.id}
```

#### 4.5 Shopper Interface Templates
Create mobile-responsive templates in `templates/shopping-lists/`:

**Main shopper interface**: `templates/shopping-lists/shopper.html`
```html
{% extends "base.html" %}

{% block title %}Shopping Lists - Restaurant CRM{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto px-4">
    <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Shopping Lists</h1>
        <p class="text-gray-600">Manage shopping lists for your organization</p>
    </div>

    <!-- Create New List Button -->
    <div class="mb-6">
        <button hx-get="/shopping-lists/create/" hx-target="#modal" hx-swap="innerHTML"
                class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
            Create New List
        </button>
    </div>

    <!-- Shopping Lists Grid -->
    <div id="shopping-lists" hx-get="/shopping-lists/" hx-trigger="load">
        <div class="animate-pulse">
            <div class="bg-white rounded-lg shadow p-6 mb-4">
                <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div class="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
        </div>
    </div>
</div>

<!-- Modal Container -->
<div id="modal"></div>
{% endblock %}

{% block scripts %}
<script>
// Refresh lists every 30 seconds
setInterval(() => {
    htmx.trigger('#shopping-lists', 'load');
}, 30000);
</script>
{% endblock %}
```

**Shopping list detail with categories**: `templates/shopping-lists/detail.html`
```html
<div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full" id="modal">
    <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold">{{ shopping_list.name }}</h2>
            <button onclick="document.getElementById('modal').remove()" 
                    class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>

        <!-- Progress Bar -->
        {% set total_items = shopping_list.categories | length %}
        {% set completed_items = shopping_list.categories | selectattr('completed_count') | list | length %}
        <div class="mb-6">
            <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>Progress</span>
                <span>{{ completed_items }}/{{ total_items }} categories completed</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-indigo-600 h-2 rounded-full transition-all duration-300" 
                     style="width: {{ (completed_items / total_items * 100) if total_items > 0 else 0 }}%"></div>
            </div>
        </div>

        <!-- Categories with Items -->
        <div class="space-y-6 max-h-96 overflow-y-auto">
            {% for category in shopping_list.categories %}
            <div class="border rounded-lg p-4">
                <div class="flex justify-between items-center mb-3">
                    <h3 class="text-lg font-semibold text-gray-900">
                        {{ category.name }}
                        <span class="text-sm text-gray-500">
                            ({{ category.completed_count }}/{{ category.total_count }})
                        </span>
                    </h3>
                    <button hx-post="/shopping-lists/{{ shopping_list.id }}/add-item/"
                            hx-target="#category-{{ category.id }}-items"
                            hx-swap="beforeend"
                            class="text-indigo-600 hover:text-indigo-800 text-sm">
                        + Add Item
                    </button>
                </div>
                
                <!-- Items List -->
                <div id="category-{{ category.id }}-items" class="space-y-2">
                    {% for item in category.items %}
                    <div class="flex items-center justify-between p-2 border rounded 
                                {% if item.is_completed %}bg-green-50 border-green-200{% else %}bg-white{% endif %}">
                        <div class="flex items-center space-x-3">
                            <input type="checkbox" 
                                   {% if item.is_completed %}checked{% endif %}
                                   hx-put="/shopping-lists/{{ shopping_list.id }}/items/{{ item.id }}/toggle/"
                                   hx-swap="outerHTML"
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                            <span class="{% if item.is_completed %}line-through text-gray-500{% endif %}">
                                {{ item.name }}
                                {% if item.quantity %} ({{ item.quantity }} {{ item.unit or 'units' }}){% endif %}
                            </span>
                        </div>
                        
                        <!-- Price Tracking Button -->
                        <button hx-get="/shopping-lists/{{ shopping_list.id }}/prices/{{ item.id }}/"
                                hx-target="#price-modal"
                                hx-swap="innerHTML"
                                class="text-gray-400 hover:text-gray-600">
                            💰
                        </button>
                    </div>
                    {% endfor %}
                </div>
                
                <!-- Add Item Form -->
                <div id="category-{{ category.id }}-form" class="mt-3 hidden">
                    <form hx-post="/shopping-lists/{{ shopping_list.id }}/items/"
                          hx-target="#category-{{ category.id }}-items"
                          hx-swap="beforeend"
                          class="flex space-x-2">
                        <input type="text" name="name" placeholder="Item name" required
                               class="flex-1 rounded-md border-gray-300">
                        <input type="text" name="quantity" placeholder="Qty" 
                               class="w-16 rounded-md border-gray-300">
                        <input type="text" name="unit" placeholder="Unit" 
                               class="w-16 rounded-md border-gray-300">
                        <button type="submit" class="bg-indigo-600 text-white px-3 py-1 rounded">
                            Add
                        </button>
                        <button type="button" onclick="this.closest('#category-{{ category.id }}-form').classList.add('hidden')"
                                class="text-gray-500 px-2">
                            Cancel
                        </button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>

<!-- Price Modal -->
<div id="price-modal"></div>

<script>
// Show add item form when button clicked
document.addEventListener('click', function(e) {
    if (e.target.textContent.includes('+ Add Item')) {
        const form = e.target.parentElement.nextElementSibling;
        if (form && form.id.includes('-form')) {
            form.classList.remove('hidden');
        }
    }
});
</script>
```

---

## Development Guidelines

### Code Quality Standards
1. **Type Hints**: All functions must have proper type annotations
2. **Docstrings**: Comprehensive docstrings for all public functions and classes
3. **Error Handling**: Proper exception handling with meaningful error messages
4. **Testing**: Minimum 80% code coverage for all modules
5. **Security**: Input validation and SQL injection prevention

### Database Guidelines
1. **Async Operations**: All database operations must be asynchronous
2. **Connection Management**: Use dependency injection for database sessions
3. **Transactions**: Proper transaction handling for multi-operation endpoints
4. **Indexing**: Index all foreign keys and frequently queried columns
5. **Migration Strategy**: Use Alembic for all database schema changes
   - All schema changes must be versioned through migrations
   - Never modify database schema directly
   - Migrations are tracked in version control
   - Use `alembic revision --autogenerate -m "description"` for new migrations
   - Apply migrations with `alembic upgrade head`
   - Rollback with `alembic downgrade -1`

### API Design Principles
1. **RESTful**: Follow REST principles for endpoint design
2. **Consistent Response Format**: Standardized success/error response structure
3. **Validation**: Server-side validation using Pydantic schemas
4. **Pagination**: Implement pagination for list endpoints
5. **Documentation**: Automatic OpenAPI documentation via FastAPI

### Frontend Guidelines
1. **HTMX Patterns**: Use HTMX for all dynamic interactions
2. **Progressive Enhancement**: Ensure basic functionality works without JavaScript
3. **Mobile-First Design**: **CRITICAL** - Design mobile interfaces first, then enhance for desktop
   - Start with 320px mobile screens and scale up
   - Test on actual mobile devices, not just browser resize
   - Ensure touch targets are minimum 44px for accessibility
   - Prioritize content hierarchy for mobile users
4. **Responsive Typography**: Use fluid typography that scales across device sizes
5. **Touch-Optimized UI**: All interactive elements must work seamlessly with touch input
6. **Responsive Data Visualization**: Complex data must remain readable on small screens
7. **Offline-Capable**: Shopper interface should function with intermittent connectivity
8. **Performance**: Optimize for fast loading on mobile networks and low-end devices
9. **Accessibility**: Follow WCAG 2.1 AA standards for all screen sizes

### Migration Best Practices
1. **Always Use Migrations**: Never modify database schema directly
2. **Descriptive Messages**: Use clear, descriptive migration names
3. **Test Migrations**: Test both upgrade and downgrade paths
4. **Review Generated Migrations**: Always review auto-generated migrations before committing
5. **Keep Migrations Small**: One logical change per migration for easier debugging
6. **Document Complex Migrations**: Add comments explaining non-obvious changes
7. **Version Control**: Commit migrations with code changes that depend on them


### Testing Strategy
1. **Unit Tests**: Test all business logic functions
2. **Integration Tests**: Test API endpoints with database operations
3. **Authentication Tests**: Comprehensive tests for auth flows
4. **Frontend Tests**: Test HTMX interactions and form submissions
5. **Performance Tests**: Load testing for critical endpoints
6. **Migration Tests**: Test database migrations in isolation

### Security Best Practices
1. **Password Hashing**: Use bcrypt for password hashing
2. **JWT Tokens**: Secure token generation and validation
3. **Input Sanitization**: Sanitize all user inputs
4. **SQL Injection Prevention**: Use parameterized queries
5. **HTTPS Only**: Enforce HTTPS in production
6. **Session Management**: Secure session handling and timeout

---

This architecture document provides a comprehensive foundation for implementing stages 1-4 of the Restaurant CRM system. Each stage builds upon the previous one, creating a solid foundation for the full system implementation.