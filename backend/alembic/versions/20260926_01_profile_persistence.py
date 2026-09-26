"""Create immutable candidate-profile persistence tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260926_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    json_document = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.create_table("candidate_profile_revisions", sa.Column("profile_id", sa.Uuid(), nullable=False), sa.Column("revision", sa.Integer(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("profile_status", sa.String(32), nullable=False), sa.Column("snapshot", json_document, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.PrimaryKeyConstraint("profile_id", "revision"))
    op.create_index("ix_candidate_profile_revisions_user_id", "candidate_profile_revisions", ["user_id"])
    op.create_table("profile_evidence", sa.Column("evidence_id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("profile_id", sa.Uuid(), nullable=False), sa.Column("profile_revision", sa.Integer(), nullable=False), sa.Column("source_type", sa.String(32), nullable=False), sa.Column("source_reference", sa.Text(), nullable=False), sa.Column("captured_claim", sa.Text(), nullable=False), sa.Column("confidence", sa.Float(), nullable=False), sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["profile_id", "profile_revision"], ["candidate_profile_revisions.profile_id", "candidate_profile_revisions.revision"]), sa.PrimaryKeyConstraint("evidence_id"))
    op.create_index("ix_profile_evidence_user_id", "profile_evidence", ["user_id"])
    op.create_table("profile_change_proposals", sa.Column("proposal_id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid(), nullable=False), sa.Column("profile_id", sa.Uuid(), nullable=False), sa.Column("base_profile_revision", sa.Integer(), nullable=False), sa.Column("operation", sa.String(16), nullable=False), sa.Column("field_path", sa.Text(), nullable=False), sa.Column("old_value", json_document), sa.Column("new_value", json_document), sa.Column("rationale", sa.Text(), nullable=False), sa.Column("evidence_ids", json_document, nullable=False), sa.Column("source_type", sa.String(32), nullable=False), sa.Column("confidence", sa.Float(), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("resolved_at", sa.DateTime(timezone=True)), sa.ForeignKeyConstraint(["profile_id", "base_profile_revision"], ["candidate_profile_revisions.profile_id", "candidate_profile_revisions.revision"]), sa.PrimaryKeyConstraint("proposal_id"))
    op.create_index("ix_profile_change_proposals_user_id", "profile_change_proposals", ["user_id"])
    op.create_index("ix_profile_change_proposals_status", "profile_change_proposals", ["status"])


def downgrade() -> None:
    op.drop_table("profile_change_proposals")
    op.drop_table("profile_evidence")
    op.drop_table("candidate_profile_revisions")
