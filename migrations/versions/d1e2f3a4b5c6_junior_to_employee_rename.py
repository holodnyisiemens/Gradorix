"""Rename JUNIOR to EMPLOYEE: enum values, enum types, table names, column names

Revision ID: d1e2f3a4b5c6
Revises: b1c2d3e4f5a6
Create Date: 2026-04-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename enum value in user_role
    op.execute("ALTER TYPE user_role RENAME VALUE 'JUNIOR' TO 'EMPLOYEE'")

    # Rename challenge_junior_progress enum type
    op.execute("ALTER TYPE challenge_junior_progress RENAME TO challenge_employee_progress")

    # Rename junior_id column in challenge_junior table
    op.execute("ALTER TABLE challenge_junior RENAME COLUMN junior_id TO employee_id")

    # Rename junior_id column in mentor_junior table
    op.execute("ALTER TABLE mentor_junior RENAME COLUMN junior_id TO employee_id")

    # Rename tables
    op.execute("ALTER TABLE challenge_junior RENAME TO challenge_employee")
    op.execute("ALTER TABLE mentor_junior RENAME TO mentor_employee")


def downgrade() -> None:
    op.execute("ALTER TABLE mentor_employee RENAME TO mentor_junior")
    op.execute("ALTER TABLE challenge_employee RENAME TO challenge_junior")

    op.execute("ALTER TABLE mentor_junior RENAME COLUMN employee_id TO junior_id")
    op.execute("ALTER TABLE challenge_junior RENAME COLUMN employee_id TO junior_id")

    op.execute("ALTER TYPE challenge_employee_progress RENAME TO challenge_junior_progress")
    op.execute("ALTER TYPE user_role RENAME VALUE 'EMPLOYEE' TO 'JUNIOR'")
