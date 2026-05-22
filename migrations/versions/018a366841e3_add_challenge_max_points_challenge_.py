"""add challenge max_points, challenge_junior fields, activity links achieved_date, quiz_result answers

Revision ID: 018a366841e3
Revises: e14a9aaed29b
Create Date: 2026-04-09 19:49:19.680939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018a366841e3'
down_revision: Union[str, Sequence[str], None] = 'e14a9aaed29b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    activities_columns = [c['name'] for c in inspector.get_columns('activities')]
    if 'links' not in activities_columns:
        op.add_column('activities', sa.Column('links', sa.JSON(), nullable=True))
    if 'achieved_date' not in activities_columns:
        op.add_column('activities', sa.Column('achieved_date', sa.Date(), nullable=True))

    challenge_junior_columns = [c['name'] for c in inspector.get_columns('challenge_junior')]
    if 'comment' not in challenge_junior_columns:
        op.add_column('challenge_junior', sa.Column('comment', sa.String(length=2000), nullable=True))
    if 'links' not in challenge_junior_columns:
        op.add_column('challenge_junior', sa.Column('links', sa.JSON(), nullable=True))
    if 'awarded_points' not in challenge_junior_columns:
        op.add_column('challenge_junior', sa.Column('awarded_points', sa.Integer(), nullable=True))
    if 'feedback' not in challenge_junior_columns:
        op.add_column('challenge_junior', sa.Column('feedback', sa.String(length=2000), nullable=True))

    challenges_columns = [c['name'] for c in inspector.get_columns('challenges')]
    if 'max_points' not in challenges_columns:
        op.add_column('challenges', sa.Column('max_points', sa.Integer(), nullable=True))

    quiz_results_columns = [c['name'] for c in inspector.get_columns('quiz_results')]
    if 'answers' not in quiz_results_columns:
        op.add_column('quiz_results', sa.Column('answers', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    quiz_results_columns = [c['name'] for c in inspector.get_columns('quiz_results')]
    if 'answers' in quiz_results_columns:
        op.drop_column('quiz_results', 'answers')

    challenges_columns = [c['name'] for c in inspector.get_columns('challenges')]
    if 'max_points' in challenges_columns:
        op.drop_column('challenges', 'max_points')

    challenge_junior_columns = [c['name'] for c in inspector.get_columns('challenge_junior')]
    if 'feedback' in challenge_junior_columns:
        op.drop_column('challenge_junior', 'feedback')
    if 'awarded_points' in challenge_junior_columns:
        op.drop_column('challenge_junior', 'awarded_points')
    if 'links' in challenge_junior_columns:
        op.drop_column('challenge_junior', 'links')
    if 'comment' in challenge_junior_columns:
        op.drop_column('challenge_junior', 'comment')

    activities_columns = [c['name'] for c in inspector.get_columns('activities')]
    if 'achieved_date' in activities_columns:
        op.drop_column('activities', 'achieved_date')
    if 'links' in activities_columns:
        op.drop_column('activities', 'links')
    # ### end Alembic commands ###
