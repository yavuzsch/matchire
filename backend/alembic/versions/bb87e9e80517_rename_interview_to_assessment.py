"""rename interview to assessment

Revision ID: bb87e9e80517
Revises: 88be3acf8b8c
Create Date: 2026-08-26 23:35:09.726469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb87e9e80517'
down_revision: Union[str, Sequence[str], None] = '88be3acf8b8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("interview_questions", "assessment_questions")
    op.rename_table("interview_answers", "assessment_answers")

    op.alter_column("jobs", "interview_slots", new_column_name="assessment_slots")
    op.alter_column("jobs", "interview_weight", new_column_name="assessment_weight")
    op.alter_column("applications", "interview_score", new_column_name="assessment_score")

    op.execute("ALTER TYPE applicationstatus RENAME VALUE 'INTERVIEW' TO 'ASSESSMENT'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE applicationstatus RENAME VALUE 'ASSESSMENT' TO 'INTERVIEW'")

    op.alter_column("applications", "assessment_score", new_column_name="interview_score")
    op.alter_column("jobs", "assessment_weight", new_column_name="interview_weight")
    op.alter_column("jobs", "assessment_slots", new_column_name="interview_slots")

    op.rename_table("assessment_answers", "interview_answers")
    op.rename_table("assessment_questions", "interview_questions")
    # ### end Alembic commands ###
