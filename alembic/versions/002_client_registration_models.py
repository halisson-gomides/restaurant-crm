"""Client registration models migration

Revision ID: 002
Revises: 
Create Date: 2025-10-31 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create client registration models."""
    # Create addresses table
    op.create_table('addresses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('cep', sa.String(9), nullable=False),
        sa.Column('endereco', sa.Text(), nullable=False),
        sa.Column('bairro', sa.String(100), nullable=True),
        sa.Column('cidade', sa.String(100), nullable=False),
        sa.Column('estado', sa.String(2), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_addresses_cep'), 'addresses', ['cep'], unique=False)

    # Create registration_sessions table
    op.create_table('registration_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('session_id', sa.String(255), nullable=False),
        sa.Column('registration_type', sa.String(10), nullable=False),
        sa.Column('step', sa.Integer(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('data', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index(op.f('ix_registration_sessions_session_id'), 'registration_sessions', ['session_id'], unique=True)

    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('cnpj', sa.String(18), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('trade_name', sa.String(255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('cnpj_registration_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cnpj'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_organizations_cnpj'), 'organizations', ['cnpj'], unique=True)
    op.create_index(op.f('ix_organizations_email'), 'organizations', ['email'], unique=True)

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('username', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=True),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('registration_type', sa.String(10), nullable=True),
        sa.Column('registration_data', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create user_roles table
    op.create_table('user_roles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_user_roles_organization_id'), 'user_roles', ['organization_id'], unique=False)
    op.create_index(op.f('ix_user_roles_user_id'), 'user_roles', ['user_id'], unique=False)

    # Create cnpj_registrations table
    op.create_table('cnpj_registrations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('qual_seu_negocio', sa.String(100), nullable=False),
        sa.Column('cnpj', sa.String(18), nullable=False),
        sa.Column('razao_social', sa.String(255), nullable=False),
        sa.Column('seu_nome', sa.String(255), nullable=False),
        sa.Column('sua_funcao', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('celular', sa.String(20), nullable=False),
        sa.Column('terms_accepted', sa.Boolean(), nullable=True),
        sa.Column('marketing_opt_in', sa.Boolean(), nullable=True),
        sa.Column('cep', sa.String(9), nullable=False),
        sa.Column('endereco', sa.Text(), nullable=False),
        sa.Column('bairro', sa.String(100), nullable=False),
        sa.Column('cidade', sa.String(100), nullable=False),
        sa.Column('estado', sa.String(2), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cnpj'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_cnpj_registrations_cnpj'), 'cnpj_registrations', ['cnpj'], unique=True)
    op.create_index(op.f('ix_cnpj_registrations_email'), 'cnpj_registrations', ['email'], unique=True)

    # Create cpf_registrations table
    op.create_table('cpf_registrations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('perfil_compra', sa.String(20), nullable=False),
        sa.Column('qual_negocio_cpf', sa.String(255), nullable=True),
        sa.Column('cpf', sa.String(14), nullable=False),
        sa.Column('nome_completo', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('genero', sa.String(20), nullable=False),
        sa.Column('celular', sa.String(20), nullable=False),
        sa.Column('data_nascimento', sa.Date(), nullable=False),
        sa.Column('terms_accepted', sa.Boolean(), nullable=True),
        sa.Column('marketing_opt_in', sa.Boolean(), nullable=True),
        sa.Column('cep', sa.String(9), nullable=False),
        sa.Column('endereco', sa.Text(), nullable=False),
        sa.Column('bairro', sa.String(100), nullable=False),
        sa.Column('cidade', sa.String(100), nullable=False),
        sa.Column('estado', sa.String(2), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cpf'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_cpf_registrations_cpf'), 'cpf_registrations', ['cpf'], unique=True)
    op.create_index(op.f('ix_cpf_registrations_email'), 'cpf_registrations', ['email'], unique=True)

    # Create foreign key constraints
    op.create_foreign_key(
        'fk_organizations_cnpj_registration_id', 
        'organizations', 
        'cnpj_registrations',
        ['cnpj_registration_id'],
        ['id'],
        ondelete='SET NULL'
    )

    


def downgrade() -> None:
    """Drop client registration models."""
    op.drop_table('cpf_registrations')
    op.drop_table('cnpj_registrations')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('organizations')
    op.drop_table('registration_sessions')
    op.drop_table('addresses')