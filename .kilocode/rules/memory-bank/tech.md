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
- **Payment Processing**: Stripe integration

### Frontend Technologies
- **Template Engine**: Jinja2
- **Dynamic Interactions**: HTMX
- **Styling**: CSS framework (TBD)
- **Design Requirements**: Clean, sober, elegant interface

### Development Tools
- **Testing**: Pytest framework
- **Version Control**: Git
- **Containerization**: Docker + Docker Compose
- **Development Container**: VSCode devcontainer

### Dependency Management
- **Python Dependencies**: Managed via `pyproject.toml`
- **Virtual Environment**: Managed through uv
- **Build System**: uv-based project management

### Key Dependencies (Planned)
- **FastAPI**: Web framework
- **asyncpg**: PostgreSQL async driver
- **python-jose**: JWT handling
- **stripe**: Payment processing
- **pytest**: Testing framework
- **pydantic**: Data validation
- **sqlalchemy**: ORM (optional, depending on approach)
- **uvicorn**: ASGI server

## Development Workflow

### Project Structure (Planned)
```
restaurant-crm/
├── src/                    # Source code
├── tests/                  # Test files
├── migrations/             # Database migrations
├── static/                 # Static assets
├── templates/              # Jinja2 templates
├── config/                 # Configuration files
└── docs/                   # Documentation
```

### Development Stages
1. **Stage 1**: Initial project setup (environment, dependencies, folder structure)
2. **Stage 2**: Client Form Register implementation
3. **Stage 3**: Authentication system and profile control
4. **Stage 4**: Restaurant Shopping List implementation
5. **Stage 5**: Stripe integration for subscription management
6. **Stage 6**: Inventory control and shopping list integration
7. **Stage 7**: POS development and tax receipt issuance
8. **Stage 8**: Dashboard with KPIs development
9. **Stage 9**: Reports section creation
10. **Stage 10**: Testing and final adjustments

### Build and Run Commands
- **Development Server**: `uvicorn main:app --reload --host 0.0.0.0 --port 8001`
- **Database Migrations**: `alembic upgrade head`
- **Testing**: `pytest`
- **Package Installation**: `uv sync`

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