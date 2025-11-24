"""add_ai_feedback_to_answers

Revision ID: cf63f973b9ad
Revises: 362dd136c4ca
Create Date: 2025-11-22 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf63f973b9ad'
down_revision = '362dd136c4ca'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add ai_feedback column to answers table
    op.add_column('answers', sa.Column('ai_feedback', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove ai_feedback column
    op.drop_column('answers', 'ai_feedback')
