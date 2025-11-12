# Restaurant CRM - Technical Stack

## Development Environment

### Container Setup
- **Docker**: Complete development environment using Docker Compose
- **Base Image**: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- **Development Ports**:
  - Application: 8001
  - PostgreSQL: 5432
- **Container Names**:
  - App container: `app-restaurant`
  - Database container: `db-restaurant`

### Database Configuration
- **Database**: PostgreSQL 17
- **Database Name**: `restaurant_crm`
- **User**: `postgres`
- **Password**: `postgres`
- **Volume**: `postgres-data` for persistent storage

## Technology Stack

### Backend Technologies
- **Framework**: FastAPI (Python)
- **Python Version**: 3.12+
- **Package Manager**: uv
- **Database**: PostgreSQL with async operations
- **Authentication**: Session-based with role validation
- **Payment Processing**: Stripe integration (Stage 5 planned)
- **Migration System**: Alembic with async support
- **Validation**: Pydantic models
- **Password Hashing**: bcrypt via passlib

### Frontend Technologies
- **Template Engine**: Jinja2
- **Dynamic Interactions**: HTMX
- **Styling**: CSS framework (TBD)
- **Design Requirements**: Clean, sober, elegant interface
- **JavaScript**: Vanilla JS for HTMX interactions
- **Responsive Design**: Mobile-first approach

### Development Tools
- **Testing**: Pytest framework
- **Version Control**: Git
- **Containerization**: Docker + Docker Compose
- **Development Container**: VSCode devcontainer
- **Migration Management**: Alembic

### Dependency Management
- **Python Dependencies**: Managed via `pyproject.toml`
- **Virtual Environment**: Managed through uv
- **Build System**: uv-based project management

### Key Dependencies (Implemented)
- **FastAPI**: Web framework ✅ Implemented
- **asyncpg**: PostgreSQL async driver ✅ Implemented
- **python-jose**: JWT handling ✅ Framework ready (Stage 3)
- **stripe**: Payment processing ⏳ Stage 5
- **pytest**: Testing framework ✅ Implemented
- **pydantic**: Data validation ✅ Implemented
- **sqlalchemy**: ORM with async support ✅ Implemented
- **uvicorn**: ASGI server ✅ Implemented
- **httpx**: HTTP client for external APIs ✅ Implemented (ViaCEP)
- **passlib**: Password hashing ✅ Implemented
- **alembic**: Database migrations ✅ Implemented

## Development Workflow

### Project Structure (Implemented)
```
restaurant-crm/
├── src/                    # Source code
│   ├── main.py            # FastAPI application entry point ✅
│   ├── config.py          # Configuration management ✅
│   ├── database.py        # Database connection and session ✅
│   ├── models/            # SQLAlchemy models ✅
│   │   ├── __init__.py    # Model imports ✅
│   │   ├── base.py        # Base model class ✅
│   │   └── client_registration.py # Registration models ✅
│   ├── schemas/           # Pydantic schemas ✅
│   │   ├── __init__.py
│   │   └── client_registration.py # Registration schemas ✅
│   ├── services/          # Business logic layer ✅
│   │   ├── __init__.py
│   │   ├── base_service.py # Base service class ✅
│   │   └── client_registration_service.py # Registration service ✅
│   ├── api/               # API routes ✅
│   │   ├── __init__.py
│   │   ├── deps.py        # Dependencies (auth, database) ✅
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── registration.py # Registration endpoints ✅
│   └── utils/             # Utility functions ✅
│       ├── __init__.py
│       ├── helpers.py     # Helper functions ✅
│       └── templates.py   # Template utilities ✅
├── templates/             # Jinja2 templates ✅
│   ├── base.html          # Base template ✅
│   └── registration/      # Registration templates ✅
├── static/                # Static assets ✅
│   ├── css/style.css      # Styling ✅
│   └── js/stage2.js       # Registration JavaScript ✅
├── tests/                 # Test files ✅
├── alembic/               # Database migrations ✅
│   ├── env.py             # Alembic environment configuration ✅
│   ├── alembic.ini        # Alembic configuration ✅
│   └── versions/          # Migration scripts ✅
├── docs/                  # Documentation ✅
├── pyproject.toml         # Project configuration ✅
├── pytest.ini             # Pytest configuration ✅
└── alembic.ini            # Alembic root configuration ✅
```

### Development Stages (Current Status)
1. **Stage 1**: ✅ Complete (Initial project setup with comprehensive database schema)
2. **Stage 2**: ✅ Complete (Client Form Register - CNPJ/CPF registration system - FULLY IMPLEMENTED AND FUNCTIONAL)
3. **Stage 3**: 🔄 Next (Authentication System implementation)
4. **Stage 4**: ⏳ Planned (Restaurant Shopping List implementation)
5. **Stage 5**: ⏳ Planned (Stripe integration for subscription management)
6. **Stage 6**: ⏳ Planned (Inventory control and shopping list integration)
7. **Stage 7**: ⏳ Planned (POS development and tax receipt issuance)
8. **Stage 8**: ⏳ Planned (Dashboard with KPIs development)
9. **Stage 9**: ⏳ Planned (Reports section creation)
10. **Stage 10**: ⏳ Planned (Testing and final adjustments)

### Stage 2 Implementation Details ✅ COMPLETE
- **CNPJ Registration**: Full 2-step registration flow with business validation
- **CPF Registration**: Full 2-step registration flow with individual validation
- **Brazilian Document Validation**: Official CNPJ/CPF algorithms implemented
- **ViaCEP Integration**: Address autocomplete from Brazilian postal codes
- **Email Validation**: Real-time uniqueness checking for both registration types
- **Mobile-First UI**: Responsive templates with HTMX dynamic interactions
- **Database Schema**: 7 tables created with proper relationships and constraints
- **Migration System**: Alembic migrations rebuilt from scratch and verified
- **Testing**: 90+ test cases with comprehensive validation coverage
- **Brazilian Localization**: Complete formatting for documents, phones, dates

### Build and Run Commands (Verified Working)
- **Development Server**: `uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8001`
- **Database Migrations**: `uv run alembic upgrade head`
- **Testing**: `uv run pytest`
- **Package Installation**: `uv sync`
- **Migration Management**: `uv run alembic revision --autogenerate -m "description"`
- **Database Reset**: `uv run alembic downgrade base && uv run alembic upgrade head`

## Constraints and Considerations

### Performance Requirements
- **Async Operations**: All database operations must be asynchronous
- **Response Time**: Sub-second response times for critical operations
- **Scalability**: Support for multiple restaurant locations
- **Concurrent Users**: Handle multiple simultaneous users

### Security Requirements
- **Role-based Access**: Strict RBAC implementation
- **Data Protection**: Secure handling of financial and business data
- **Session Management**: Secure session handling
- **API Security**: Protected endpoints with validation

### Development Constraints
- **Clean Architecture**: Maintain separation of concerns
- **Code Quality**: Comprehensive testing required
- **Documentation**: Complete code and architecture documentation
- **Iterative Development**: Prefer partial deliveries over big-bang approach