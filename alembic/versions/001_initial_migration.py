"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create organizations table FIRST (no dependencies)
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('bin', sa.String(length=12), nullable=False),
        sa.Column('company_address', sa.String(length=500), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('bin')
    )
    op.create_index(op.f('ix_organizations_deleted_at'), 'organizations', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=True)

    # Create users table SECOND (references organizations)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('iin', sa.String(length=12), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('AUTHORITY_ADMIN', 'ORGANIZATION_ADMIN', 'ORGANIZATION_PILOT', 'SOLO_PILOT', name='userrole'), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_user_organization_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone_number'),
        sa.UniqueConstraint('iin')
    )
    op.create_index(op.f('ix_users_deleted_at'), 'users', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_iin'), 'users', ['iin'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)

    # Now add the admin_id foreign key to organizations (circular reference)
    op.create_foreign_key('fk_organization_admin_id', 'organizations', 'users', ['admin_id'], ['id'])

    # Create drones table
    op.create_table('drones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('serial_number', sa.String(length=100), nullable=False),
        sa.Column('owner_type', sa.Enum('ORGANIZATION', 'SOLO_PILOT', name='droneownertype'), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('solo_owner_user_id', sa.Integer(), nullable=True),
        sa.Column('current_status', sa.Enum('IDLE', 'ACTIVE', 'MAINTENANCE', 'UNKNOWN', name='dronestatus'), nullable=False, server_default='IDLE'),
        sa.Column('last_telemetry_id', sa.BigInteger(), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_drone_organization_id'),
        sa.ForeignKeyConstraint(['solo_owner_user_id'], ['users.id'], name='fk_drone_solo_owner_user_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial_number')
    )
    op.create_index(op.f('ix_drones_deleted_at'), 'drones', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_drones_id'), 'drones', ['id'], unique=False)
    op.create_index(op.f('ix_drones_serial_number'), 'drones', ['serial_number'], unique=True)


def downgrade() -> None:
    op.drop_table('drones')
    op.drop_table('users')
    op.drop_table('organizations')
