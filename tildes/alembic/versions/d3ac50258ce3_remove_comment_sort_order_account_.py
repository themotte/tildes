"""Remove comment sort order account setting

Revision ID: d3ac50258ce3
Revises: 4d86b372a8db
Create Date: 2020-07-03 18:51:47.836251

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d3ac50258ce3"
down_revision = "4d86b372a8db"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("users", "comment_sort_order_default")
    op.execute("drop type commenttreesortoption")


def downgrade():
    op.execute(
        "create type commenttreesortoption as enum('VOTES', 'NEWEST', 'POSTED', 'RELEVANCE')"
    )
    op.add_column(
        "users",
        sa.Column(
            "comment_sort_order_default",
            postgresql.ENUM(
                "VOTES", "NEWEST", "POSTED", "RELEVANCE", name="commenttreesortoption"
            ),
            nullable=True,
        ),
    )
