# Alembic Database Migration Setup

## Overview

Alembic is a lightweight database migration tool for SQLAlchemy. It provides version control for database schemas, allowing you to track and apply schema changes systematically.

## Setup Status

✅ **Alembic is fully configured and ready to use**

### Completed Setup Steps

1. ✅ Installed Alembic 1.17.1 (via `uv sync --all-extras`)
2. ✅ Initialized Alembic directory structure
3. ✅ Configured `alembic.ini` with PostgreSQL async connection
4. ✅ Updated `alembic/env.py` for async database operations
5. ✅ Created initial migration template

## Project Structure

```
alembic/
├── versions/                    # Migration scripts directory
│   └── 001_initial_schema.py   # Initial migration template
├── env.py                       # Alembic environment configuration (async-enabled)
├── script.py.mako              # Migration script template
├── README                       # Alembic README
└── alembic.ini                 # Alembic configuration file
```

## Configuration Details

### Database Connection

**File**: `alembic.ini` (line 87)

```ini
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/restaurant_crm
```

- **Driver**: `postgresql+asyncpg` (async PostgreSQL driver)
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `restaurant_crm`
- **User**: `postgres`
- **Password**: `postgres`

### Async Support

**File**: `alembic/env.py`

The environment is configured for async operations:

- Uses `create_async_engine()` for async database connections
- Implements `asyncio.run()` for async migration execution
- Supports both online and offline migration modes
- Compatible with `asyncpg` driver

## Common Commands

### Check Current Migration Status

```bash
uv run alembic current
```

Shows the current database revision.

### View Migration History

```bash
uv run alembic history
```

Lists all applied migrations.

### Create Auto-Generated Migration

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

Automatically generates migration based on model changes.

### Create Empty Migration

```bash
uv run alembic revision -m "Description of changes"
```

Creates an empty migration for manual editing.

### Apply Migrations (Upgrade)

```bash
uv run alembic upgrade head
```

Applies all pending migrations to the database.

### Rollback Migration (Downgrade)

```bash
uv run alembic downgrade -1
```

Rolls back the last applied migration.

### Rollback to Specific Revision

```bash
uv run alembic downgrade <revision_id>
```

Rolls back to a specific migration revision.

## Workflow for Adding Models

### Step 1: Define Your Model

Create a new model in `src/models/` directory:

```python
from src.models.base import BaseModel
from sqlalchemy import Column, String

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
```

### Step 2: Register Model in Alembic

Update `alembic/env.py` to include your models:

```python
# Line 20-21 in alembic/env.py
from src.models.base import Base
from src.models.user import User  # Import your model

target_metadata = Base.metadata
```

### Step 3: Generate Migration

```bash
uv run alembic revision --autogenerate -m "Add users table"
```

This creates a new migration file in `alembic/versions/`.

### Step 4: Review Migration

Open the generated migration file and verify the SQL changes are correct.

### Step 5: Apply Migration

```bash
uv run alembic upgrade head
```

## Migration File Structure

Each migration file contains:

```python
"""Description of changes.

Revision ID: 002
Revises: 001
Create Date: 2025-10-30 20:44:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_table('users')
```

## Best Practices

### 1. Always Review Generated Migrations

Auto-generated migrations may not always be perfect. Review and adjust as needed.

### 2. Use Descriptive Revision Messages

```bash
# Good
uv run alembic revision --autogenerate -m "Add email verification to users"

# Avoid
uv run alembic revision --autogenerate -m "Update"
```

### 3. Keep Migrations Atomic

Each migration should represent a single logical change.

### 4. Test Migrations

Always test migrations in a development environment before applying to production.

### 5. Never Modify Applied Migrations

Once a migration is applied to production, never modify it. Create a new migration instead.

### 6. Use Offline Mode for SQL Generation

Generate SQL without applying it:

```bash
uv run alembic upgrade head --sql
```

## Troubleshooting

### Issue: "No such table: alembic_version"

**Solution**: The migration table hasn't been created yet. Run:

```bash
uv run alembic upgrade head
```

### Issue: "Can't locate revision identified by 'xxx'"

**Solution**: Ensure the revision ID exists in `alembic/versions/`.

### Issue: Async Connection Errors

**Solution**: Verify the database is running and the connection string in `alembic.ini` is correct.

### Issue: "Target database is not up to date"

**Solution**: Run pending migrations:

```bash
uv run alembic upgrade head
```

## Integration with FastAPI

The migration system integrates with the FastAPI application:

1. **Database Setup**: `src/database.py` creates the async engine
2. **Models**: All models inherit from `BaseModel` in `src/models/base.py`
3. **Migrations**: Alembic tracks all schema changes

## Next Steps

1. Define your data models in `src/models/`
2. Update `alembic/env.py` to import your models
3. Generate migrations with `alembic revision --autogenerate`
4. Apply migrations with `alembic upgrade head`
5. Continue development with confidence in schema versioning

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [PostgreSQL asyncpg Driver](https://magicstack.github.io/asyncpg/)
