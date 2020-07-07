"""Add topic pinned column

Revision ID: 2c50cb4dd1b8
Revises: d3ac50258ce3
Create Date: 2020-07-07 05:55:16.035347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c50cb4dd1b8"
down_revision = "d3ac50258ce3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "topics",
        sa.Column("is_pinned", sa.Boolean(), server_default="false", nullable=False),
    )


def downgrade():
    op.drop_column("topics", "is_pinned")
