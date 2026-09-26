"""Persist globally shared raw jobs, canonical jobs, and job profiles."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260926_02"
down_revision = "20260926_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    document = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.create_table("raw_jobs", sa.Column("raw_job_id", sa.Uuid(), nullable=False), sa.Column("source_name", sa.String(128), nullable=False), sa.Column("external_id", sa.String(256), nullable=False), sa.Column("source_url", sa.Text(), nullable=False), sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False), sa.Column("content_hash", sa.String(256), nullable=False), sa.Column("snapshot", document, nullable=False), sa.PrimaryKeyConstraint("raw_job_id"))
    op.create_index("ix_raw_jobs_content_hash", "raw_jobs", ["content_hash"])
    op.create_table("jobs", sa.Column("job_id", sa.Uuid(), nullable=False), sa.Column("canonical_key", sa.String(512), nullable=False), sa.Column("snapshot", document, nullable=False), sa.PrimaryKeyConstraint("job_id"), sa.UniqueConstraint("canonical_key"))
    op.create_table("job_profile_revisions", sa.Column("job_profile_id", sa.Uuid(), nullable=False), sa.Column("job_id", sa.Uuid(), nullable=False), sa.Column("revision", sa.Integer(), nullable=False), sa.Column("raw_job_id", sa.Uuid(), nullable=False), sa.Column("analysed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("snapshot", document, nullable=False), sa.ForeignKeyConstraint(["job_id"], ["jobs.job_id"]), sa.ForeignKeyConstraint(["raw_job_id"], ["raw_jobs.raw_job_id"]), sa.PrimaryKeyConstraint("job_profile_id"), sa.UniqueConstraint("job_id", "revision", name="uq_job_profile_revision"))
    op.create_index("ix_job_profile_revisions_job_id", "job_profile_revisions", ["job_id"])


def downgrade() -> None:
    op.drop_table("job_profile_revisions")
    op.drop_table("jobs")
    op.drop_table("raw_jobs")
