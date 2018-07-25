"""Add topic pinned column

Revision ID: ec4b50c96a8e
Revises: 2512581c91b3
Create Date: 2018-07-25 18:47:13.724735

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ec4b50c96a8e'
down_revision = '2512581c91b3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('topics', sa.Column('is_pinned', sa.Boolean(), server_default='false', nullable=False))


def downgrade():
    op.drop_column('topics', 'is_pinned')
