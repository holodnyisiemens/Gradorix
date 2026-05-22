"""points for calendar events

Revision ID: 917e1a7848e2
Revises: a62da1b4aa1f
Create Date: 2026-05-22 09:16:59.164943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '917e1a7848e2'
down_revision: Union[str, Sequence[str], None] = 'a62da1b4aa1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('meeting_attendance')]

    if 'awarded_points' not in columns:
        op.add_column('meeting_attendance', sa.Column('awarded_points', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('meeting_attendance')]

    if 'awarded_points' in columns:
        op.drop_column('meeting_attendance', 'awarded_points')
