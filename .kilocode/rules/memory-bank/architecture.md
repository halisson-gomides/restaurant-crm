# Restaurant CRM - System Architecture

## System Overview
The Restaurant CRM follows a modern web architecture pattern with backend API services, frontend templating, and database integration. The system is designed for scalability and multi-location restaurant chain operations.

## High-Level Architecture

### Application Layers
1. **Frontend Layer**: Jinja2 templating with HTMX for dynamic interactions
2. **API Layer**: FastAPI framework providing REST endpoints
3. **Business Logic Layer**: Core business rules and workflows
4. **Data Access Layer**: Asynchronous PostgreSQL operations
5. **Database Layer**: PostgreSQL database with async support

### Core Components

#### User Management System ✅ IMPLEMENTED (Stage 1-2)
- **Authentication**: Role-based access control (Framework ready)
- **User Profiles**: CPF (employees), CNPJ (corporate customers) ✅ Complete
- **Role Hierarchy**: Administrator, Manager, Employee, Shopper, Customer ✅ Defined
- **Client Registration**: Full CNPJ/CPF registration system ✅ Complete

#### Shopping List Management 🔄 STAGE 4 (Planned)
- **Category Organization**: Proteins, fruits/vegetables, dairy, cleaning, groceries, packaging
- **Supplier Management**: Supermarket registration and price tracking
- **Shopper Interface**: Mobile-responsive list management

#### Inventory Control System 🔄 STAGE 6 (Planned)
- **Real-time Tracking**: Integration with shopping list purchases
- **Multi-location Support**: Centralized inventory with location-specific controls
- **Automatic Updates**: Purchase-to-inventory workflow

#### Point of Sale (POS) 🔄 STAGE 7 (Planned)
- **Order Management**: Dining room, delivery, kitchen operations
- **Receipt Generation**: Tax-compliant receipt issuance
- **Integration**: Connected to inventory and sales analytics

#### Analytics & Reporting 🔄 STAGES 8-9 (Planned)
- **KPI Dashboard**: Daily, weekly, monthly performance metrics
- **Sales Reports**: Category-based analysis and billing reports
- **Predictive Analytics**: AI-powered forecasting and trend analysis

#### Subscription Management 🔄 STAGE 5 (Planned)
- **Payment Processing**: Stripe integration for subscription billing
- **Plan Management**: Subscription tiers and payment handling
- **Notification System**: Payment and subscription status updates

## Data Model ✅ IMPLEMENTED (Stage 2)

### Core Entities ✅ Complete
- **Organizations**: Restaurant companies (CNPJ-based) ✅ Implemented
- **Users**: People with role-based access ✅ Implemented
- **Addresses**: Brazilian address management ✅ Implemented
- **CNPJ Registrations**: Corporate customer registration ✅ Implemented
- **CPF Registrations**: Individual customer registration ✅ Implemented
- **Registration Sessions**: Multi-step form state management ✅ Implemented
- **User Roles**: Multi-role support per user ✅ Implemented

### Key Relationships ✅ Complete
- Organizations ↔ Users (many-to-many with roles) ✅ Implemented
- User Roles: User ↔ Organization relationships ✅ Implemented
- Address relationships for CNPJ/CPF registrations ✅ Implemented

### Database Schema Status ✅ Complete (Stage 2)
**Tables Created:**
1. `addresses` - Brazilian address storage
2. `cnpj_registrations` - Corporate customer data
3. `cpf_registrations` - Individual customer data
4. `registration_sessions` - Multi-step form state
5. `organizations` - Restaurant companies
6. `users` - System users
7. `user_roles` - Role-based access control

**Migration Status**: ✅ Active (alembic/versions/93160675bbfa_initial_database_schema.py)

## Security Architecture 🔄 STAGE 3 (In Progress)
- **Authentication**: JWT-based authentication (Framework ready)
- **Authorization**: Role-based access control (RBAC) (Models ready)
- **Data Protection**: Secure handling of business and financial data
- **API Security**: Protected endpoints with role validation

## Integration Points ✅ IMPLEMENTED
- **ViaCEP API**: Address lookup integration ✅ Complete (Stage 2)
- **PostgreSQL**: Primary database with async operations ✅ Complete
- **HTMX**: Frontend interactivity without full SPA framework ✅ Complete
- **Jinja2**: Template rendering and dynamic content ✅ Complete
- **AsyncPG**: PostgreSQL async driver ✅ Complete

## Scalability Considerations
- **Multi-location Support**: Centralized data with location-based filtering ✅ Architecture ready
- **Async Operations**: PostgreSQL async for concurrent request handling ✅ Implemented
- **Modular Design**: Stage-based implementation allows incremental scaling ✅ Implemented
- **Performance Optimization**: Database indexing and query optimization ✅ Implemented

## Development Status
- **Stage 1**: ✅ Complete (Initial project setup)
- **Stage 2**: ✅ Complete (Client Registration System)
- **Stage 3**: 🔄 Next (Authentication System)
- **Stage 4+**: ⏳ Planned (Shopping Lists, POS, Analytics, etc.)