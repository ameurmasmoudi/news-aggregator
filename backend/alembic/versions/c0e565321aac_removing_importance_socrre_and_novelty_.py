"""removing importance socrre and novelty and adding life_impact, stage and people_affected_stated to clusters

Revision ID: c0e565321aac
Revises: d934d8a054f4
Create Date: 2026-09-01 03:40:35.877517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0e565321aac'
down_revision: Union[str, Sequence[str], None] = 'd934d8a054f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("clusters", sa.Column("life_impact", sa.String(20), nullable=True))
    op.add_column("clusters", sa.Column("stage", sa.String(20), nullable=True))
    op.add_column("clusters", sa.Column(
        "people_affected_stated", sa.Integer(), nullable=False, server_default="0"))
    op.drop_column("clusters", "importance_score")
    op.drop_column("clusters", "novelty")

def downgrade():
    op.add_column("clusters", sa.Column("novelty", sa.String(10), nullable=True))
    op.add_column("clusters", sa.Column("importance_score", sa.Integer(), nullable=True))
    op.drop_column("clusters", "people_affected_stated")
    op.drop_column("clusters", "stage")
    op.drop_column("clusters", "life_impact")

