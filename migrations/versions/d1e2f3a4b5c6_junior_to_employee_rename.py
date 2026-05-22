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
    op.execute("""
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'user_role'
    ) AND EXISTS (
        SELECT 1 FROM unnest(enum_range(NULL::user_role)) x WHERE x::text = 'JUNIOR'
    ) THEN
        ALTER TYPE user_role RENAME VALUE 'JUNIOR' TO 'EMPLOYEE';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'challenge_junior_progress'
    ) THEN
        ALTER TYPE challenge_junior_progress RENAME TO challenge_employee_progress;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'challenge_junior' AND column_name = 'junior_id'
    ) THEN
        ALTER TABLE challenge_junior RENAME COLUMN junior_id TO employee_id;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'mentor_junior' AND column_name = 'junior_id'
    ) THEN
        ALTER TABLE mentor_junior RENAME COLUMN junior_id TO employee_id;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_name = 'challenge_junior'
    ) THEN
        ALTER TABLE challenge_junior RENAME TO challenge_employee;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_name = 'mentor_junior'
    ) THEN
        ALTER TABLE mentor_junior RENAME TO mentor_employee;
    END IF;
END
$$;
""")


def downgrade() -> None:
    op.execute("""
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_name = 'mentor_employee'
    ) THEN
        ALTER TABLE mentor_employee RENAME TO mentor_junior;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_name = 'challenge_employee'
    ) THEN
        ALTER TABLE challenge_employee RENAME TO challenge_junior;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'mentor_junior' AND column_name = 'employee_id'
    ) THEN
        ALTER TABLE mentor_junior RENAME COLUMN employee_id TO junior_id;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'challenge_junior' AND column_name = 'employee_id'
    ) THEN
        ALTER TABLE challenge_junior RENAME COLUMN employee_id TO junior_id;
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'challenge_employee_progress'
    ) THEN
        ALTER TYPE challenge_employee_progress RENAME TO challenge_junior_progress;
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'user_role'
    ) AND EXISTS (
        SELECT 1 FROM unnest(enum_range(NULL::user_role)) x WHERE x::text = 'EMPLOYEE'
    ) THEN
        ALTER TYPE user_role RENAME VALUE 'EMPLOYEE' TO 'JUNIOR';
    END IF;
END
$$;
""")
