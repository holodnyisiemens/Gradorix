"""Merge heads 917e1a7848e2 and d1e2f3a4b5c6

Revision ID: merge_917e1a7848e2_d1e2f3a4b5c6
Revises: 917e1a7848e2, d1e2f3a4b5c6
Create Date: 2026-05-22 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'merge_917e1a7848e2_d1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = ('917e1a7848e2', 'd1e2f3a4b5c6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge branch heads."""
    pass


def downgrade() -> None:
    """Downgrade merge."""
    pass
