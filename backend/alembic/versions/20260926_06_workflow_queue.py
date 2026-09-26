"""Create durable PostgreSQL workflow queue."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260926_06"
down_revision = "20260926_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    document = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.create_table(
        "workflow_tasks",
        sa.Column("task_id", sa.Uuid(), primary_key=True),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_name", sa.String(128), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("error_code", sa.String(128)),
        sa.Column("payload", document, nullable=False),
    )
    op.create_index("ix_workflow_tasks_workflow_run_id", "workflow_tasks", ["workflow_run_id"])
    op.create_index("ix_workflow_tasks_workflow_name", "workflow_tasks", ["workflow_name"])
    op.create_index("ix_workflow_tasks_status", "workflow_tasks", ["status"])
    op.create_index("ix_workflow_tasks_available_at", "workflow_tasks", ["available_at"])


def downgrade() -> None:
    op.drop_table("workflow_tasks")
