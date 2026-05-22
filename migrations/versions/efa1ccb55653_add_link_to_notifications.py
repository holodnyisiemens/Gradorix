"""add link to notifications

Revision ID: efa1ccb55653
Revises: c0636a96c06a
Create Date: 2026-04-24 11:19:11.930764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efa1ccb55653'
down_revision: Union[str, Sequence[str], None] = 'c0636a96c06a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('notifications')]

    if 'link' not in columns:
        op.add_column('notifications', sa.Column('link', sa.String(length=2048), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('notifications')]

    if 'link' in columns:
        op.drop_column('notifications', 'link')
