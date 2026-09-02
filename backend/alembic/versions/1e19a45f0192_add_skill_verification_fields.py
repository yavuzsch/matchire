"""add skill verification fields

Revision ID: 1e19a45f0192
Revises: 33d58bac2a02
Create Date: 2026-09-02 20:56:11.955951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e19a45f0192'
down_revision: Union[str, Sequence[str], None] = '33d58bac2a02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('skills', sa.Column('is_verified', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('skills', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_skills_created_by_users', 'skills', 'users', ['created_by'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_skills_created_by_users', 'skills', type_='foreignkey')
    op.drop_column('skills', 'created_by')
    op.drop_column('skills', 'is_verified')
    # ### end Alembic commands ###
