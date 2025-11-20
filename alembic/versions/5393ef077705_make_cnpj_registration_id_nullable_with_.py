"""Make cnpj_registration_id nullable with SET NULL on delete

Revision ID: 5393ef077705
Revises: 93160675bbfa
Create Date: 2025-11-20 15:36:03.043381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5393ef077705'
down_revision: Union[str, Sequence[str], None] = '93160675bbfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing foreign key constraint
    op.drop_constraint('organizations_cnpj_registration_id_fkey', 'organizations', type_='foreignkey')

    # Alter the column to be nullable
    op.alter_column('organizations', 'cnpj_registration_id',
                    existing_type=sa.String(),
                    nullable=True)

    # Add the new foreign key constraint with ON DELETE SET NULL
    op.create_foreign_key(
        'organizations_cnpj_registration_id_fkey',
        'organizations', 'cnpj_registrations',
        ['cnpj_registration_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the foreign key constraint
    op.drop_constraint('organizations_cnpj_registration_id_fkey', 'organizations', type_='foreignkey')

    # Alter the column back to not nullable
    op.alter_column('organizations', 'cnpj_registration_id',
                    existing_type=sa.String(),
                    nullable=False)

    # Add the original foreign key constraint
    op.create_foreign_key(
        'organizations_cnpj_registration_id_fkey',
        'organizations', 'cnpj_registrations',
        ['cnpj_registration_id'], ['id']
    )
