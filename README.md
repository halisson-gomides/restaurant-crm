# Restaurant CRM

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17+-blue.svg)](https://www.postgresql.org/)

A comprehensive Customer Relationship Management (CRM) system specifically designed for restaurant chains, providing end-to-end business management capabilities including inventory control, point-of-sale operations, subscription management, and predictive analytics.

## 🚀 Features

### Core Functionality ✅ **IMPLEMENTED**
- **Client Registration**: Corporate customer management with CNPJ/company ID integration and CPF individual registration
- **Admin Management System**: Full admin dashboard with registration management, statistics, and data export capabilities
- **Authentication System**: JWT-based admin authentication with role-based access control

### Core Functionality 🔄 **IN DEVELOPMENT**
- **Shopping List Management**: Category-organized shopping lists (proteins, produce, dairy, cleaning products, packaging, groceries)
- **Subscription Management**: Stripe integration for payment processing and subscription handling
- **Inventory Control**: Complete inventory management integrated with shopping lists
- **Point of Sale (POS)**: Full POS functionality with tax receipt generation
- **Analytics Dashboard**: KPI tracking with daily, weekly, monthly reporting
- **Comprehensive Reports**: Billing, tax, and sales analysis by category
- **Predictive Analytics**: AI-powered sales forecasting and consumption trend analysis

### Technical Features ✅ **IMPLEMENTED**
- **Multi-location Support**: Database schema designed for multi-location restaurant chains
- **Real-time Updates**: HTMX-powered dynamic frontend interactions
- **Mobile-responsive Interface**: Responsive templates optimized for mobile shopping list management
- **Async Database Operations**: High-performance asynchronous PostgreSQL operations
- **Role-based Security**: JWT authentication and admin management system
- **Brazilian Localization**: Complete CNPJ/CPF validation, formatting, and ViaCEP integration

## 🛠 Technology Stack

### Backend ✅ **IMPLEMENTED**
- **Python 3.12+**: Core programming language
- **FastAPI**: Modern web framework for building APIs
- **PostgreSQL 17**: Primary database with async operations
- **SQLAlchemy (Async)**: Python SQL toolkit and ORM
- **Alembic**: Database migrations with async support
- **JWT Authentication**: Secure token-based authentication system
- **Pydantic**: Data validation and serialization

### Frontend ✅ **IMPLEMENTED**
- **Jinja2**: Template engine for server-side rendering
- **HTMX**: Dynamic interactions for enhanced user experience
- **JQuery JavaScript**: Minimal JavaScript for form interactions and validation
- **CSS Framework**: Custom responsive styling with mobile-first approach
- **Progressive Enhancement**: Works without JavaScript, enhanced with it

### Development & Deployment ✅ **IMPLEMENTED**
- **Docker**: Complete containerized development environment
- **uv**: Fast Python package manager
- **Pytest**: Testing framework with async support
- **Black**: Python code formatter
- **Pre-commit**: Git hooks for code quality
- **Alembic**: Database migration management

## 🏗 Architecture

The Restaurant CRM follows a modern layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Admin     │  │ Registration│  │ Future UI   │        │
│  │   UI        │  │    UI       │  │ Components  │        │
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
│  │  │ Auth Routes │ │ Registration│ │ Future      │    │  │
│  │  │             │ │    Routes   │ │    Routes   │    │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Business Logic Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Auth      │  │ Client      │  │ Future      │        │
│  │  Service    │  │Registration │  │   Services  │        │
│  │             │  │   Service   │  │             │        │
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
│  │  Organizations • Users • Registrations • More...    │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Development Roadmap

### Stage 1: Initial Project Setup ✅ **COMPLETE**
- [x] Project structure and development environment
- [x] Database configuration and dependencies (7 tables with async operations)
- [x] Foundation architecture components
- [x] Testing framework setup with pytest
- [x] Alembic migration system

### Stage 2: Client Form Register ✅ **COMPLETE**
- [x] CNPJ/company registration system with Brazilian validation
- [x] CPF/individual registration system
- [x] 2-step registration forms with progressive validation
- [x] ViaCEP integration for address autocomplete
- [x] Email uniqueness validation
- [x] reCAPTCHA integration for security
- [x] Mobile-responsive registration templates
- [x] Complete form validation and error handling

### Stage 2.1: Admin Management System ✅ **COMPLETE**
- [x] Admin authentication with JWT tokens
- [x] Admin dashboard with statistics overview
- [x] Registration management interface (view, edit, search, export)
- [x] Advanced filtering and pagination
- [x] Data export functionality (Excel)
- [x] Role-based access control for admin functions

### Stage 3: Enhanced Authentication System 🔄 **NEXT**
- [ ] User registration and profile management
- [ ] Role-based permissions and access control
- [ ] Secure session management middleware
- [ ] Protected routes and authentication dependencies
- [ ] Password reset and account recovery functionality

### Stage 4: Restaurant Shopping List 🔄 **PLANNED**
- [ ] Category management system
- [ ] Shopping list CRUD operations
- [ ] Shopper interface with price tracking
- [ ] Mobile-responsive UI for field use

### Stage 5: Subscription Management 📋 **PLANNED**
- [ ] Stripe integration for payment processing
- [ ] Subscription plan management
- [ ] Payment handling and notifications

### Stage 6: Inventory Control 📋 **PLANNED**
- [ ] Complete inventory management
- [ ] Shopping list integration
- [ ] Real-time stock tracking

### Stage 7: Point of Sale (POS) 📋 **PLANNED**
- [ ] Full POS functionality
- [ ] Tax receipt generation
- [ ] Order management (dining room, delivery, kitchen)

### Stage 8: Analytics Dashboard 📋 **PLANNED**
- [ ] KPI tracking and reporting
- [ ] Daily, weekly, monthly metrics
- [ ] Interactive dashboards

### Stage 9: Reports & Predictive Analytics 📋 **PLANNED**
- [ ] Comprehensive reporting system
- [ ] Sales analysis by category
- [ ] AI-powered forecasting

### Stage 10: Testing & Finalization 📋 **PLANNED**
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
   - **Admin Login**: http://localhost:8001/auth/login
   - **Registration**: http://localhost:8001/registration
   - **API Documentation**: http://localhost:8001/docs
   - **Database**: localhost:5432

### Development Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

# Run tests
uv run pytest

# Run migrations
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
```

## 🔐 Security

### Authentication & Authorization ✅ **IMPLEMENTED**
- JWT-based authentication with secure token handling
- Admin role-based access control for management functions
- Password hashing using bcrypt
- Session management with automatic expiration

### Data Protection ✅ **IMPLEMENTED**
- Input validation and sanitization via Pydantic
- SQL injection prevention through SQLAlchemy ORM
- reCAPTCHA integration for bot protection
- Secure configuration management via environment variables

### API Security ✅ **IMPLEMENTED**
- Protected admin endpoints with authentication requirements
- Request validation and error handling
- CORS configuration for secure cross-origin requests
- Role-based middleware for admin functions

## 📊 Database Schema ✅ **IMPLEMENTED**

### Core Entities
- **addresses**: Brazilian address information
- **cnpj_registrations**: Company registration records
- **cpf_registrations**: Individual registration records
- **organizations**: Restaurant companies (CNPJ-based)
- **registration_sessions**: Multi-step registration state management
- **users**: System users with roles
- **user_roles**: Multi-role support for users

### Key Features ✅ **COMPLETE**
- **Brazilian Localization**: Complete CNPJ/CPF validation algorithms
- **Address Management**: ViaCEP integration for Brazilian postal codes
- **Multi-step Registration**: Session-based form state management
- **Data Integrity**: Foreign key constraints and unique indexes
- **Async Operations**: Full async/await support for high performance

## 🧪 Testing

The project uses pytest with async support for comprehensive testing:

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_auth.py

# Run with verbose output
uv run pytest -v
```

### Test Structure ✅ **IMPLEMENTED**
- **Registration Tests**: CNPJ/CPF validation and form handling
- **Authentication Tests**: JWT token handling and admin login
- **Database Tests**: Async ORM operations and migrations
- **Integration Tests**: API endpoint testing with database
- **Security Tests**: reCAPTCHA validation and data protection

## 📚 Documentation

### Architecture Documentation ✅ **IMPLEMENTED**
- [Software Architecture](docs/software-architecture.md) - Comprehensive technical architecture
- [Stage 1 Completion](docs/STAGE_1_COMPLETION.md) - Initial setup documentation
- [Stage 2 Completion](docs/STAGE_2_COMPLETION.md) - Registration system documentation
- [Alembic Setup Guide](docs/ALEMBIC_SETUP.md) - Database migration guide
- [API Documentation](http://localhost:8001/docs) - Interactive API docs (when running)

### Code Documentation ✅ **IMPLEMENTED**
- All public functions include comprehensive docstrings
- Type hints for all function signatures
- Inline comments for complex business logic
- Brazilian business logic documentation

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

---

**Restaurant CRM** - Streamlining restaurant operations with modern technology solutions.