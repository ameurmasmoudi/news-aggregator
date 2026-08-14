"""text_fields_fix

Revision ID: 1870d9e92305
Revises: 8e66352abacb
Create Date: 2026-08-12 22:37:10.823827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1870d9e92305'
down_revision: Union[str, Sequence[str], None] = '8e66352abacb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.alter_column('clusters', 'one_sentence_summary', type_=sa.Text(), existing_nullable=True)
    op.alter_column('clusters', 'why_important', type_=sa.Text(), existing_nullable=True)
    op.alter_column('clusters', 'recommended_action', type_=sa.Text(), existing_nullable=True)

def downgrade():
    op.alter_column('clusters', 'one_sentence_summary', type_=sa.String(200), existing_nullable=True)
    op.alter_column('clusters', 'why_important', type_=sa.String(200), existing_nullable=True)
    op.alter_column('clusters', 'recommended_action', type_=sa.String(200), existing_nullable=True)
