"""move category and summay from articles to clusters and removed article and source count

Revision ID: c667cd51ce06
Revises: 0a5c787ef19c
Create Date: 2026-07-27 01:29:20.240946

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c667cd51ce06'
down_revision: Union[str, Sequence[str], None] = '0a5c787ef19c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clusters", sa.Column("category", sa.String(50)))
    op.drop_column("clusters","source_count")
    op.drop_column("clusters","article_count")
    op.drop_column("articles","category")
    op.drop_column("articles","summary")
    
    pass


def downgrade() -> None:
    op.drop_column("clusters","category")
    op.add_column("clusters", sa.Column("source_count", sa.Integer()))
    op.add_column("clusters", sa.Column("article_count", sa.Integer()))
    op.add_column("articles", sa.Column("summary", sa.String(50)))
    op.add_column("articles", sa.Column("category", sa.String(50)))
    pass
