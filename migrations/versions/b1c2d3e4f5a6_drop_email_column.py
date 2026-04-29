"""drop email column if still exists

Revision ID: b1c2d3e4f5a6
Revises: a3f1b2c4d5e6
Create Date: 2026-04-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'a3f1b2c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS email")


def downgrade() -> None:
    pass
