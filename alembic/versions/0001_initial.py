"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-12-18 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'events',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('user_email', sa.String, nullable=True),
        sa.Column('total_uploaded', sa.Integer, default=0),
        sa.Column('total_selected', sa.Integer, default=0),
        sa.Column('processing_status', sa.String, default='pending'),
        sa.Column('processed_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'images',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('event_id', sa.Integer, sa.ForeignKey('events.id')),
        sa.Column('filename', sa.String, nullable=True),
        sa.Column('filepath', sa.String, nullable=True),
        sa.Column('uploaded_at', sa.DateTime, nullable=True),
        sa.Column('quality_score', sa.Float, default=0.0),
        sa.Column('sharpness_score', sa.Float, default=0.0),
        sa.Column('brightness_score', sa.Float, default=0.0),
        sa.Column('contrast_score', sa.Float, default=0.0),
        sa.Column('is_blur', sa.Boolean, default=False),
        sa.Column('is_duplicate', sa.Boolean, default=False),
        sa.Column('is_selected', sa.Boolean, default=False),
        sa.Column('is_posted', sa.Boolean, default=False),
    )

    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('event_id', sa.Integer, sa.ForeignKey('events.id')),
        sa.Column('posted_at', sa.DateTime, nullable=True),
        sa.Column('linkedin_post_id', sa.String, nullable=True),
        sa.Column('num_images', sa.Integer, default=0),
        sa.Column('status', sa.String, default='pending'),
        sa.Column('error_message', sa.String, nullable=True),
    )

    op.create_table(
        'linkedin_tokens',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_email', sa.String, nullable=True),
        sa.Column('access_token', sa.String, nullable=True),
        sa.Column('refresh_token', sa.String, nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )


def downgrade():
    op.drop_table('linkedin_tokens')
    op.drop_table('posts')
    op.drop_table('images')
    op.drop_table('events')
