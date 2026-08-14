"""make_pusbhlished_at_timezone_aware

Revision ID: 8e66352abacb
Revises: c667cd51ce06
Create Date: 2026-08-12 16:10:13.317854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e66352abacb'
down_revision: Union[str, Sequence[str], None] = 'c667cd51ce06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('articles', 'published_at',
        type_=sa.TIMESTAMP(timezone=True), existing_nullable=True)
    op.alter_column('clusters', 'latest_published_at',
        type_=sa.TIMESTAMP(timezone=True), existing_nullable=True)
    op.alter_column('clusters', 'created_at',
        type_=sa.TIMESTAMP(timezone=True), existing_nullable=False)
    op.alter_column('clusters', 'updated_at',
        type_=sa.TIMESTAMP(timezone=True), existing_nullable=False)

def downgrade():
    op.alter_column('articles', 'published_at',
        type_=sa.TIMESTAMP(timezone=False), existing_nullable=True)
    op.alter_column('clusters', 'latest_published_at',
        type_=sa.TIMESTAMP(timezone=False), existing_nullable=True)
    op.alter_column('clusters', 'created_at',
        type_=sa.TIMESTAMP(timezone=False), existing_nullable=False)
    op.alter_column('clusters', 'updated_at',
        type_=sa.TIMESTAMP(timezone=False), existing_nullable=False)
