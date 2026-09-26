"""Persist user-scoped fit assessments."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260926_03"
down_revision = "20260926_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    document = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.create_table("assessments", sa.Column("assessment_id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("job_id", sa.Uuid(), nullable=False), sa.Column("assessment_type", sa.String(16), nullable=False), sa.Column("assessed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("snapshot", document, nullable=False), sa.PrimaryKeyConstraint("assessment_id"))
    op.create_index("ix_assessments_user_id", "assessments", ["user_id"])
    op.create_index("ix_assessments_job_id", "assessments", ["job_id"])


def downgrade() -> None:
    op.drop_table("assessments")
