"""add missing indexes

Revision ID: add_missing_indexes
Revises: None
Create Date: 2026-05-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_indexes'
down_revision = '0001_baseline'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add indexes for foreign key performance optimization
    op.create_index(op.f('ix_channels_user_id'), 'channels', ['user_id'], unique=False)
    op.create_index(op.f('ix_competitors_channel_id'), 'competitors', ['channel_id'], unique=False)
    op.create_index(op.f('ix_scripts_user_id'), 'scripts', ['user_id'], unique=False)
    op.create_index(op.f('ix_videos_channel_id'), 'videos', ['channel_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_videos_channel_id'), table_name='videos')
    op.drop_index(op.f('ix_scripts_user_id'), table_name='scripts')
    op.drop_index(op.f('ix_competitors_channel_id'), table_name='competitors')
    op.drop_index(op.f('ix_channels_user_id'), table_name='channels')
