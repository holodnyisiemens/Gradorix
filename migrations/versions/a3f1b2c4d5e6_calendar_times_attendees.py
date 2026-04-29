"""calendar: add times, created_by, attendees table

Revision ID: a3f1b2c4d5e6
Revises: a62da1b4aa1f
Create Date: 2026-04-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f1b2c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'a62da1b4aa1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('calendar_events', sa.Column('start_time', sa.Time(), nullable=True))
    op.add_column('calendar_events', sa.Column('end_time', sa.Time(), nullable=True))
    op.add_column('calendar_events', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_calendar_events_created_by',
        'calendar_events', 'users',
        ['created_by'], ['id'],
        ondelete='SET NULL',
    )
    op.create_table(
        'calendar_event_attendees',
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['calendar_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id', 'user_id'),
    )


def downgrade() -> None:
    op.drop_table('calendar_event_attendees')
    op.drop_constraint('fk_calendar_events_created_by', 'calendar_events', type_='foreignkey')
    op.drop_column('calendar_events', 'created_by')
    op.drop_column('calendar_events', 'end_time')
    op.drop_column('calendar_events', 'start_time')
