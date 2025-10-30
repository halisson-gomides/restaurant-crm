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

#### User Management System
- **Authentication**: Role-based access control
- **User Profiles**: CPF (employees), CNPJ (corporate customers)
- **Role Hierarchy**: Administrator, Manager, Employee, Shopper, Customer

#### Shopping List Management
- **Category Organization**: Proteins, fruits/vegetables, dairy, cleaning, groceries, packaging
- **Supplier Management**: Supermarket registration and price tracking
- **Shopper Interface**: Mobile-responsive list management

#### Inventory Control System
- **Real-time Tracking**: Integration with shopping list purchases
- **Multi-location Support**: Centralized inventory with location-specific controls
- **Automatic Updates**: Purchase-to-inventory workflow

#### Point of Sale (POS)
- **Order Management**: Dining room, delivery, kitchen operations
- **Receipt Generation**: Tax-compliant receipt issuance
- **Integration**: Connected to inventory and sales analytics

#### Analytics & Reporting
- **KPI Dashboard**: Daily, weekly, monthly performance metrics
- **Sales Reports**: Category-based analysis and billing reports
- **Predictive Analytics**: AI-powered forecasting and trend analysis

#### Subscription Management
- **Payment Processing**: Stripe integration for subscription billing
- **Plan Management**: Subscription tiers and payment handling
- **Notification System**: Payment and subscription status updates

## Data Model

### Core Entities
- **Organizations**: Restaurant companies (CNPJ-based)
- **Users**: People with role-based access
- **Shopping Lists**: Categorized procurement lists
- **Supermarkets**: Price comparison sources
- **Inventory Items**: Stock management entities
- **Orders**: POS transaction records
- **Subscriptions**: Payment plan management

### Key Relationships
- Organizations ↔ Users (many-to-many with roles)
- Shopping Lists → Categories → Items
- Inventory ↔ Shopping Lists (purchase flow)
- Orders → POS Transactions → Receipts

## Security Architecture
- **Authentication**: Session-based authentication
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: Secure handling of business and financial data
- **API Security**: Protected endpoints with role validation

## Integration Points
- **Stripe API**: Payment processing and subscription management
- **PostgreSQL**: Primary database with async operations
- **HTMX**: Frontend interactivity without full SPA framework
- **Jinja2**: Template rendering and dynamic content

## Scalability Considerations
- **Multi-location Support**: Centralized data with location-based filtering
- **Async Operations**: PostgreSQL async for concurrent request handling
- **Modular Design**: Stage-based implementation allows incremental scaling
- **Performance Optimization**: Database indexing and query optimization