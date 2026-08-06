"""add pgvector

Revision ID: 0a5c787ef19c
Revises: 339afed0157e
Create Date: 2026-07-26 15:25:01.514136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0a5c787ef19c'
down_revision: Union[str, Sequence[str], None] = '339afed0157e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column("clusters", sa.Column("vector", Vector(768)))
    pass


def downgrade() -> None:
    op.drop_column("clusters", "vector")
    op.execute("drop extension if exists vector")
    pass
