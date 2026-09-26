"""Persist append-only workflow and agent execution audit records."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260926_05"
down_revision = "20260926_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    document = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.create_table(
        "workflow_run_revisions",
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("workflow_name", sa.String(128), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("trace_id", sa.Uuid(), nullable=False),
        sa.Column("scope", sa.String(16), nullable=False),
        sa.Column("user_id", sa.Uuid()),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("snapshot", document, nullable=False),
        sa.PrimaryKeyConstraint("workflow_run_id", "revision"),
    )
    op.create_index(
        "ix_workflow_run_revisions_workflow_name", "workflow_run_revisions", ["workflow_name"]
    )
    op.create_index(
        "ix_workflow_run_revisions_correlation_id", "workflow_run_revisions", ["correlation_id"]
    )
    op.create_index("ix_workflow_run_revisions_trace_id", "workflow_run_revisions", ["trace_id"])
    op.create_index("ix_workflow_run_revisions_user_id", "workflow_run_revisions", ["user_id"])
    op.create_index("ix_workflow_run_revisions_status", "workflow_run_revisions", ["status"])
    op.create_table(
        "agent_runs",
        sa.Column("agent_run_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("agent_name", sa.String(128), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("snapshot", document, nullable=False),
        sa.PrimaryKeyConstraint("agent_run_id"),
    )
    op.create_index("ix_agent_runs_workflow_run_id", "agent_runs", ["workflow_run_id"])
    op.create_index("ix_agent_runs_agent_name", "agent_runs", ["agent_name"])
    op.create_index("ix_agent_runs_status", "agent_runs", ["status"])


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("workflow_run_revisions")
