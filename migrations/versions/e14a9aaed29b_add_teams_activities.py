"""add teams & activities

Revision ID: e14a9aaed29b
Revises: f973559c9dca
Create Date: 2026-03-24 21:01:48.776363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e14a9aaed29b'
down_revision: Union[str, Sequence[str], None] = 'f973559c9dca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if 'achievements' not in tables:
        op.create_table('achievements',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('description', sa.String(length=1000), nullable=False),
            sa.Column('icon', sa.String(length=10), nullable=False),
            sa.Column('category', sa.Enum('MILESTONE', 'CHALLENGE', 'STREAK', 'SOCIAL', 'SPECIAL', name='achievement_category'), nullable=False),
            sa.Column('xp', sa.Integer(), server_default='0', nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
    if 'kb_sections' not in tables:
        op.create_table('kb_sections',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('order', sa.Integer(), server_default='0', nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
    if 'quizzes' not in tables:
        op.create_table('quizzes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('description', sa.String(length=1000), nullable=False),
            sa.Column('category', sa.String(length=100), nullable=False),
            sa.Column('duration_min', sa.Integer(), server_default='10', nullable=False),
            sa.Column('questions', sa.JSON(), nullable=False),
            sa.Column('points', sa.Integer(), server_default='0', nullable=False),
            sa.Column('available', sa.Boolean(), server_default='true', nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
    if 'activities' not in tables:
        op.create_table('activities',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('description', sa.String(length=1000), nullable=False),
            sa.Column('requested_points', sa.Integer(), nullable=False),
            sa.Column('awarded_points', sa.Integer(), nullable=True),
            sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'REVISION', name='activity_status'), nullable=False),
            sa.Column('activity_type', sa.Enum('ACHIEVEMENT', 'TASK', 'TEST', 'EVENT', 'CUSTOM', name='activity_type'), nullable=False),
            sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('review_note', sa.String(length=1000), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    if 'calendar_events' not in tables:
        op.create_table('calendar_events',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('event_type', sa.Enum('CHALLENGE', 'MEETING', 'DEADLINE', name='calendar_event_type'), nullable=False),
            sa.Column('challenge_id', sa.Integer(), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
    if 'challenge_junior' not in tables:
        op.create_table('challenge_junior',
            sa.Column('challenge_id', sa.Integer(), nullable=False),
            sa.Column('junior_id', sa.Integer(), nullable=False),
            sa.Column('assigned_by', sa.Integer(), nullable=False),
            sa.Column('progress', sa.Enum('GOING', 'IN_PROGRESS', 'DONE', 'SKIPPED', name='challenge_junior_progress'), nullable=False),
            sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['junior_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('challenge_id', 'junior_id')
        )
    if 'kb_articles' not in tables:
        op.create_table('kb_articles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('section_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('created_at', sa.Date(), nullable=False),
            sa.Column('author', sa.String(length=100), nullable=False),
            sa.ForeignKeyConstraint(['section_id'], ['kb_sections.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    if 'quiz_results' not in tables:
        op.create_table('quiz_results',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('quiz_id', sa.Integer(), nullable=False),
            sa.Column('score', sa.Integer(), nullable=False),
            sa.Column('completed_at', sa.Date(), nullable=False),
            sa.Column('points_earned', sa.Integer(), server_default='0', nullable=False),
            sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    if 'teams' not in tables:
        op.create_table('teams',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('project', sa.String(length=255), nullable=False),
            sa.Column('status', sa.Enum('ACTIVE', 'ON_HOLD', 'COMPLETED', name='team_status'), nullable=False),
            sa.Column('mentor_id', sa.Integer(), nullable=True),
            sa.Column('description', sa.String(length=1000), nullable=False),
            sa.ForeignKeyConstraint(['mentor_id'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
    if 'user_achievements' not in tables:
        op.create_table('user_achievements',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('achievement_id', sa.Integer(), nullable=False),
            sa.Column('earned_at', sa.Date(), nullable=True),
            sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('user_id', 'achievement_id')
        )
    if 'user_points' not in tables:
        op.create_table('user_points',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('total_points', sa.Integer(), server_default='0', nullable=False),
            sa.Column('level', sa.Integer(), server_default='1', nullable=False),
            sa.Column('level_name', sa.String(length=50), nullable=False),
            sa.Column('points_to_next_level', sa.Integer(), server_default='100', nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('user_id')
        )
    if 'meeting_attendance' not in tables:
        op.create_table('meeting_attendance',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('event_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('attended', sa.Boolean(), server_default='false', nullable=False),
            sa.Column('marked_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('marked_by', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['event_id'], ['calendar_events.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['marked_by'], ['users.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    if 'team_members' not in tables:
        op.create_table('team_members',
            sa.Column('team_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('team_id', 'user_id')
        )

    challenges_columns = [c['name'] for c in inspector.get_columns('challenges')]
    if 'date' not in challenges_columns:
        op.add_column('challenges', sa.Column('date', sa.Date(), nullable=True))

    notifications_columns = [c['name'] for c in inspector.get_columns('notifications')]
    if 'created_at' not in notifications_columns:
        op.add_column('notifications', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    notifications_columns = [c['name'] for c in inspector.get_columns('notifications')] if 'notifications' in tables else []
    if 'created_at' in notifications_columns:
        op.drop_column('notifications', 'created_at')

    challenges_columns = [c['name'] for c in inspector.get_columns('challenges')] if 'challenges' in tables else []
    if 'date' in challenges_columns:
        op.drop_column('challenges', 'date')

    if 'team_members' in tables:
        op.drop_table('team_members')
    if 'meeting_attendance' in tables:
        op.drop_table('meeting_attendance')
    if 'user_points' in tables:
        op.drop_table('user_points')
    if 'user_achievements' in tables:
        op.drop_table('user_achievements')
    if 'teams' in tables:
        op.drop_table('teams')
    if 'quiz_results' in tables:
        op.drop_table('quiz_results')
    if 'kb_articles' in tables:
        op.drop_table('kb_articles')
    if 'challenge_junior' in tables:
        op.drop_table('challenge_junior')
    if 'calendar_events' in tables:
        op.drop_table('calendar_events')
    if 'activities' in tables:
        op.drop_table('activities')
    if 'quizzes' in tables:
        op.drop_table('quizzes')
    if 'kb_sections' in tables:
        op.drop_table('kb_sections')
    if 'achievements' in tables:
        op.drop_table('achievements')
    # ### end Alembic commands ###
