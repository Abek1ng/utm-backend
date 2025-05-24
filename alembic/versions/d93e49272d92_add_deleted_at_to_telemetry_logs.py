
"""Add deleted_at to telemetry_logs

Revision ID: [new_revision_id]
Revises: b621379b2521
Create Date: [current_date]

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd93e49272d92'
down_revision = 'b621379b2521'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add deleted_at column to telemetry_logs if it doesn't exist
    op.add_column('telemetry_logs', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_telemetry_logs_deleted_at'), 'telemetry_logs', ['deleted_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_telemetry_logs_deleted_at'), table_name='telemetry_logs')
    op.drop_column('telemetry_logs', 'deleted_at')