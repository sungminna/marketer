"""Add Phase 2 and Phase 3 features

Revision ID: 002
Revises: 001
Create Date: 2025-11-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create webhooks table
    op.create_table('webhooks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('events', postgresql.JSONB, nullable=False),
        sa.Column('secret', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create webhook_logs table
    op.create_table('webhook_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('webhook_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('webhooks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSONB, nullable=False),
        sa.Column('response_status_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('delivered', sa.Boolean(), default=False),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_webhook_logs_created_at'), 'webhook_logs', ['created_at'])

    # Create batch_jobs table
    op.create_table('batch_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('batch_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), default='pending'),
        sa.Column('total_jobs', sa.Integer(), default=0),
        sa.Column('completed_jobs', sa.Integer(), default=0),
        sa.Column('failed_jobs', sa.Integer(), default=0),
        sa.Column('total_cost_usd', sa.DECIMAL(10, 4), default=0),
        sa.Column('job_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), default=[]),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('batch_config', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_batch_jobs_created_at'), 'batch_jobs', ['created_at'])

    # Create templates table
    op.create_table('templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_type', sa.String(length=50), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('config', postgresql.JSONB, nullable=False),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('tags', postgresql.JSONB, default=[]),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_templates_created_at'), 'templates', ['created_at'])

    # Create teams table
    op.create_table('teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('max_members', sa.Integer(), default=10),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create team_members table
    op.create_table('team_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=50), default='member'),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('team_id', 'user_id', name='uix_team_user'),
    )

    # Create team_invitations table
    op.create_table('team_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), default='member'),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(length=255), unique=True, nullable=False),
        sa.Column('status', sa.String(length=50), default='pending'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_team_invitations_token'), 'team_invitations', ['token'])

    # Create daily_analytics table
    op.create_table('daily_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('total_jobs', sa.Integer(), default=0),
        sa.Column('successful_jobs', sa.Integer(), default=0),
        sa.Column('failed_jobs', sa.Integer(), default=0),
        sa.Column('total_quantity', sa.Integer(), default=0),
        sa.Column('total_cost_usd', sa.DECIMAL(10, 4), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_daily_analytics_date'), 'daily_analytics', ['date'])

    # Create user_quotas table
    op.create_table('user_quotas',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('plan_type', sa.String(length=50), nullable=False),
        sa.Column('monthly_image_limit', sa.Integer(), default=100),
        sa.Column('monthly_video_seconds_limit', sa.Integer(), default=60),
        sa.Column('monthly_cost_limit_usd', sa.DECIMAL(10, 2), default=10.00),
        sa.Column('reset_day', sa.Integer(), default=1),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create quota_usage table
    op.create_table('quota_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('month', sa.DateTime(), nullable=False),
        sa.Column('images_used', sa.Integer(), default=0),
        sa.Column('video_seconds_used', sa.Integer(), default=0),
        sa.Column('cost_used_usd', sa.DECIMAL(10, 4), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_quota_usage_month'), 'quota_usage', ['month'])


def downgrade() -> None:
    op.drop_table('quota_usage')
    op.drop_table('user_quotas')
    op.drop_table('daily_analytics')
    op.drop_table('team_invitations')
    op.drop_table('team_members')
    op.drop_table('teams')
    op.drop_table('templates')
    op.drop_table('batch_jobs')
    op.drop_table('webhook_logs')
    op.drop_table('webhooks')
