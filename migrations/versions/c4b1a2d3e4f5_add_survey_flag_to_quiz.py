"""add survey flag to quiz

Revision ID: c4b1a2d3e4f5
Revises: f973559c9dca
Create Date: 2026-05-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4b1a2d3e4f5'
down_revision: Union[str, Sequence[str], None] = 'merge_917e1a7848e2_d1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('quizzes')]

    if 'is_survey' not in columns:
        op.add_column(
            'quizzes',
            sa.Column('is_survey', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('quizzes')]

    if 'is_survey' in columns:
        op.drop_column('quizzes', 'is_survey')
