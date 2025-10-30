# Restaurant CRM

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17+-blue.svg)](https://www.postgresql.org/)

A comprehensive Customer Relationship Management (CRM) system specifically designed for restaurant chains, providing end-to-end business management capabilities including inventory control, point-of-sale operations, subscription management, and predictive analytics.

## 🚀 Features

### Core Functionality
- **Client Registration**: Corporate customer management with CNPJ/company ID integration
- **Authentication System**: Role-based access control (administrator, manager, employee, shopper, customer)
- **Shopping List Management**: Category-organized shopping lists (proteins, produce, dairy, cleaning products, packaging, groceries)
- **Subscription Management**: Stripe integration for payment processing and subscription handling
- **Inventory Control**: Complete inventory management integrated with shopping lists
- **Point of Sale (POS)**: Full POS functionality with tax receipt generation
- **Analytics Dashboard**: KPI tracking with daily, weekly, monthly reporting
- **Comprehensive Reports**: Billing, tax, and sales analysis by category
- **Predictive Analytics**: AI-powered sales forecasting and consumption trend analysis

### Technical Features
- **Multi-location Support**: Centralized data with location-based filtering
- **Real-time Updates**: Instant synchronization across all system components
- **Mobile-responsive Interface**: Optimized for mobile shopping list management
- **Async Database Operations**: High-performance asynchronous PostgreSQL operations
- **Role-based Security**: Secure authentication and authorization system

## 🛠 Technology Stack

### Backend
- **Python 3.12+**: Core programming language
- **FastAPI**: Modern web framework for building APIs
- **PostgreSQL 17**: Primary database with async operations
- **SQLAlchemy (Async)**: Python SQL toolkit and ORM
- **Alembic**: Database migrations
- **JWT Authentication**: Secure token-based authentication

### Frontend
- **Jinja2**: Template engine for server-side rendering
- **HTMX**: Modern frontend interactions without JavaScript complexity
- **Tailwind CSS**: Utility-first CSS framework
- **Progressive Enhancement**: Works without JavaScript, enhanced with it

### Development & Deployment
- **Docker**: Containerized development environment
- **uv**: Fast Python package manager
- **Pytest**: Testing framework with async support
- **Black**: Python code formatter
- **Pre-commit**: Git hooks for code quality

## 🏗 Architecture

The Restaurant CRM follows a modern layered architecture:

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

## 📋 Development Roadmap

### Stage 1: Initial Project Setup ✅
- [x] Project structure and development environment
- [x] Database configuration and dependencies
- [x] Foundation architecture components
- [x] Testing framework setup

### Stage 2: Client Form Register 🔄
- [ ] Organization/company registration system
- [ ] Secure user profile management
- [ ] Brazilian business ID validation (CNPJ)
- [ ] Clean, accessible forms

### Stage 3: Authentication System 🔄
- [ ] Role-based authentication system
- [ ] User profile management with CPF/CNPJ support
- [ ] Secure session management
- [ ] Protected routes and middleware

### Stage 4: Restaurant Shopping List 🔄
- [ ] Category management system
- [ ] Shopping list CRUD operations
- [ ] Shopper interface with price tracking
- [ ] Mobile-responsive UI for field use

### Stage 5: Subscription Management
- [ ] Stripe integration for payment processing
- [ ] Subscription plan management
- [ ] Payment handling and notifications

### Stage 6: Inventory Control
- [ ] Complete inventory management
- [ ] Shopping list integration
- [ ] Real-time stock tracking

### Stage 7: Point of Sale (POS)
- [ ] Full POS functionality
- [ ] Tax receipt generation
- [ ] Order management (dining room, delivery, kitchen)

### Stage 8: Analytics Dashboard
- [ ] KPI tracking and reporting
- [ ] Daily, weekly, monthly metrics
- [ ] Interactive dashboards

### Stage 9: Reports & Predictive Analytics
- [ ] Comprehensive reporting system
- [ ] Sales analysis by category
- [ ] AI-powered forecasting

### Stage 10: Testing & Finalization
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation completion

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ (if running locally)
- PostgreSQL 17+ (included in Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd restaurant-crm
   ```

2. **Start development environment**
   ```bash
   # Start all services
   docker-compose up -d
   
   # Or use VSCode Dev Containers
   # Press Ctrl+Shift+P, select "Dev Containers: Reopen in Container"
   ```

3. **Initialize database**
   ```bash
   # Run database migrations
   docker-compose exec app alembic upgrade head
   ```

4. **Access the application**
   - **Web Interface**: http://localhost:8001
   - **API Documentation**: http://localhost:8001/docs
   - **Database**: localhost:5432 (postgres/postgres)

### Development Commands

```bash
# Install dependencies
uv sync

# Run development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Run migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 📁 Project Structure

```
restaurant-crm/
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection and session
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic layer
│   ├── api/                # FastAPI routes and controllers
│   └── utils/              # Utility functions
├── templates/              # Jinja2 templates
│   ├── base.html           # Base template
│   ├── auth/               # Authentication templates
│   ├── organizations/      # Organization management
│   └── shopping-lists/     # Shopping list management
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── img/                # Images
├── tests/                  # Test files
├── alembic/                # Database migrations
├── docs/                   # Documentation
│   └── software-architecture.md  # Architecture documentation
├── .devcontainer/          # VSCode development container
├── docker-compose.yml      # Docker services
├── pyproject.toml          # Python dependencies
├── pytest.ini             # Test configuration
└── README.md               # This file
```

## 🔐 Security

### Authentication & Authorization
- JWT-based authentication with secure token handling
- Role-based access control (RBAC) for granular permissions
- Password hashing using bcrypt
- Session management with automatic expiration

### Data Protection
- Input validation and sanitization
- SQL injection prevention through parameterized queries
- HTTPS enforcement in production
- Secure configuration management

### API Security
- Protected endpoints with authentication requirements
- Rate limiting and throttling
- Request validation and error handling
- CORS configuration for secure cross-origin requests

## 📊 Database Schema

### Core Entities
- **Organizations**: Restaurant companies (CNPJ-based)
- **Users**: People with role-based access
- **Shopping Lists**: Categorized procurement lists
- **Categories**: Product categorization (proteins, produce, dairy, etc.)
- **Supermarkets**: Price comparison sources
- **Inventory Items**: Stock management entities
- **Orders**: POS transaction records
- **Subscriptions**: Payment plan management

### Key Relationships
- Organizations ↔ Users (many-to-many with roles)
- Shopping Lists → Categories → Items
- Inventory ↔ Shopping Lists (purchase flow)
- Orders → POS Transactions → Receipts

## 🧪 Testing

The project uses pytest with async support for comprehensive testing:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Structure
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints with database operations
- **Authentication Tests**: Test login/logout flows and security
- **Frontend Tests**: Test HTMX interactions and form submissions

## 📚 Documentation

### Architecture Documentation
- [Software Architecture](docs/software-architecture.md) - Comprehensive technical architecture
- [API Documentation](http://localhost:8001/docs) - Interactive API docs (when running)
- Database schema documentation in the architecture document

### Code Documentation
- All public functions include comprehensive docstrings
- Type hints for all function signatures
- Inline comments for complex business logic

## 🤝 Contributing

This is a commercial private project. For technical inquiries or collaboration opportunities, please contact the project maintainers.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Restaurant CRM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Support

For technical support, documentation, or questions:
- Review the [Software Architecture Document](docs/software-architecture.md)
- Check the interactive API documentation at `/docs` when the application is running
- Ensure your development environment is properly configured as described in the Quick Start section

---

**Restaurant CRM** - Streamlining restaurant operations with modern technology solutions.