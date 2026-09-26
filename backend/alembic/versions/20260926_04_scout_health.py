"""Persist source-health observations and idempotent raw-job revisions."""
from alembic import op
import sqlalchemy as sa

revision = "20260926_04"
down_revision = "20260926_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_raw_jobs_source_revision", "raw_jobs", ["source_name", "external_id", "content_hash"]
    )
    op.create_table("source_health", sa.Column("source_health_id", sa.Uuid(), primary_key=True), sa.Column("source_name", sa.String(128), nullable=False), sa.Column("status", sa.String(16), nullable=False), sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("item_count", sa.Integer(), nullable=False), sa.Column("latency_ms", sa.Integer(), nullable=False), sa.Column("error_code", sa.String(128)))
    op.create_index("ix_source_health_source_name", "source_health", ["source_name"])
def downgrade() -> None:
    op.drop_table("source_health")
    op.drop_constraint("uq_raw_jobs_source_revision", "raw_jobs", type_="unique")
