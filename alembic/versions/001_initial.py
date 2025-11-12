"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2025-11-12 03:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('plan_type', sa.String(50), server_default='free'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )

    # Create user_api_keys table
    op.create_table(
        'user_api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_api_keys_user_provider', 'user_api_keys', ['user_id', 'provider'], unique=True)

    # Create generation_jobs table
    op.create_table(
        'generation_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('input_params', postgresql.JSONB(), nullable=False),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('output_urls', postgresql.ARRAY(sa.Text()), server_default='{}'),
        sa.Column('cost_usd', sa.DECIMAL(10, 4), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), index=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_generation_jobs_user_status', 'generation_jobs', ['user_id', 'status'])

    # Create usage_logs table
    op.create_table(
        'usage_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('cost_usd', sa.DECIMAL(10, 4), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), index=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['generation_jobs.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_usage_logs_user_date', 'usage_logs', ['user_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('usage_logs')
    op.drop_table('generation_jobs')
    op.drop_table('user_api_keys')
    op.drop_table('users')
