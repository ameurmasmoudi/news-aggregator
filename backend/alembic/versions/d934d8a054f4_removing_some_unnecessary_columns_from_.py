"""removing some unnecessary columns from clusters

Revision ID: d934d8a054f4
Revises: 8142ea88d138
Create Date: 2026-08-16 03:04:04.290006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd934d8a054f4'
down_revision: Union[str, Sequence[str], None] = '8142ea88d138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("clusters","why_important")
    op.drop_column("clusters","event_type")
    op.drop_column("clusters","recommended_action")
 
def downgrade() -> None:
    op.add_column("clusters","why_important")
    op.add_column("clusters","event_type")
    op.add_column("clusters","recommended_action")
