"""Add remaining tables

Revision ID: b621379b2521
Revises: 001
Create Date: 2025-05-25 01:38:47.317934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b621379b2521'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_drone_assignments table
    op.create_table('user_drone_assignments',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('drone_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['drone_id'], ['drones.id'], name='fk_user_drone_assignment_drone_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_drone_assignment_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'drone_id', name='pk_user_drone_assignment')
    )

    # Create flight_plans table
    op.create_table('flight_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('drone_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('planned_departure_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('planned_arrival_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_departure_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_arrival_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('PENDING_ORG_APPROVAL', 'PENDING_AUTHORITY_APPROVAL', 'APPROVED', 'REJECTED_BY_ORG', 'REJECTED_BY_AUTHORITY', 'ACTIVE', 'COMPLETED', 'CANCELLED_BY_PILOT', 'CANCELLED_BY_ADMIN', name='flightplanstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('approved_by_organization_admin_id', sa.Integer(), nullable=True),
        sa.Column('approved_by_authority_admin_id', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by_authority_admin_id'], ['users.id'], name='fk_flight_plan_auth_admin_id'),
        sa.ForeignKeyConstraint(['approved_by_organization_admin_id'], ['users.id'], name='fk_flight_plan_org_admin_id'),
        sa.ForeignKeyConstraint(['drone_id'], ['drones.id'], name='fk_flight_plan_drone_id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_flight_plan_organization_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_flight_plan_user_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flight_plans_deleted_at'), 'flight_plans', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_flight_plans_id'), 'flight_plans', ['id'], unique=False)
    op.create_index(op.f('ix_flight_plans_status'), 'flight_plans', ['status'], unique=False)

    # Create waypoints table
    op.create_table('waypoints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flight_plan_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('altitude_m', sa.Float(), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['flight_plan_id'], ['flight_plans.id'], name='fk_waypoint_flight_plan_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_waypoint_flight_plan_id_sequence_order', 'waypoints', ['flight_plan_id', 'sequence_order'], unique=True)
    op.create_index(op.f('ix_waypoints_flight_plan_id'), 'waypoints', ['flight_plan_id'], unique=False)
    op.create_index(op.f('ix_waypoints_id'), 'waypoints', ['id'], unique=False)

    # Create telemetry_logs table
    op.create_table('telemetry_logs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('flight_plan_id', sa.Integer(), nullable=True),
    sa.Column('drone_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('altitude_m', sa.Float(), nullable=False),
    sa.Column('speed_mps', sa.Float(), nullable=True),
    sa.Column('heading_degrees', sa.Float(), nullable=True),
    sa.Column('status_message', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),  # ADD THIS LINE
    sa.ForeignKeyConstraint(['drone_id'], ['drones.id'], name='fk_telemetry_log_drone_id', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['flight_plan_id'], ['flight_plans.id'], name='fk_telemetry_log_flight_plan_id', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
)
    op.create_index(op.f('ix_telemetry_logs_drone_id'), 'telemetry_logs', ['drone_id'], unique=False)
    op.create_index(op.f('ix_telemetry_logs_flight_plan_id'), 'telemetry_logs', ['flight_plan_id'], unique=False)
    op.create_index(op.f('ix_telemetry_logs_id'), 'telemetry_logs', ['id'], unique=False)
    op.create_index(op.f('ix_telemetry_logs_timestamp'), 'telemetry_logs', ['timestamp'], unique=False)

    # Create restricted_zones table
    op.create_table('restricted_zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('geometry_type', sa.Enum('CIRCLE', 'POLYGON', name='nfzgeometrytype'), nullable=False),
        sa.Column('definition_json', sa.JSON(), nullable=False),
        sa.Column('min_altitude_m', sa.Float(), nullable=True),
        sa.Column('max_altitude_m', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by_authority_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_authority_id'], ['users.id'], name='fk_restricted_zone_creator_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_restricted_zones_deleted_at'), 'restricted_zones', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_restricted_zones_id'), 'restricted_zones', ['id'], unique=False)
    op.create_index(op.f('ix_restricted_zones_name'), 'restricted_zones', ['name'], unique=False)

    # Add the foreign key for drones.last_telemetry_id (circular reference)
    op.create_foreign_key('fk_drone_last_telemetry_id', 'drones', 'telemetry_logs', ['last_telemetry_id'], ['id'])


def downgrade() -> None:
    op.drop_table('restricted_zones')
    op.drop_table('telemetry_logs')
    op.drop_table('waypoints')
    op.drop_table('flight_plans')
    op.drop_table('user_drone_assignments')