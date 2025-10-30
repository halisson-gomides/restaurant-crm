"""Initial schema creation.

Revision ID: 001
Revises: 
Create Date: 2025-10-30 20:44:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # This is a placeholder for the initial schema.
    # Run `alembic revision --autogenerate -m "Initial schema"` to generate
    # actual migrations based on your models.
    pass


def downgrade() -> None:
    """Downgrade database schema."""
    pass
