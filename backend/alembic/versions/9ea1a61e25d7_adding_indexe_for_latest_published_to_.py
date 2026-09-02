"""adding indexe for latest_published to clusters

Revision ID: 9ea1a61e25d7
Revises: c0e565321aac
Create Date: 2026-09-01 03:53:02.278233

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ea1a61e25d7'
down_revision: Union[str, Sequence[str], None] = 'c0e565321aac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_clusters_latest_published_at","clusters",[sa.text("latest_published_at DESC")])

def downgrade() -> None:
    op.drop_index("ix_clusters_latest_published_at",table_name="clusters")
