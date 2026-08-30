"""User-scoped assessment, recommendation and feedback contracts."""

from enum import Enum
from typing import Annotated

from pydantic import Field

from .common import (
    EvidenceReference,
    PositiveRevision,
    StableId,
    UserScopedContract,
    UtcTimestamp,
)
from .profile import ConfidenceScore

type NonEmptyText = Annotated[str, Field(min_length=1)]
type AssessmentScore = Annotated[int, Field(ge=0, le=100)]


class AssessmentType(str, Enum):
    """The purpose of a user-specific assessment."""

    FIT = "FIT"
    CAREER = "CAREER"


class RecommendationClassification(str, Enum):
    """Operational shortlist category assigned by deterministic ranking policy."""

    PRIORITY = "PRIORITY"
    CONSIDER = "CONSIDER"
    EXCLUDE = "EXCLUDE"


class FeedbackAction(str, Enum):
    """The documented feedback vocabulary for a job recommendation."""

    INTERESTED = "INTERESTED"
    MAYBE = "MAYBE"
    IGNORE = "IGNORE"
    APPLIED = "APPLIED"
    NOT_RELEVANT = "NOT_RELEVANT"
    NEVER_SHOW_SIMILAR = "NEVER_SHOW_SIMILAR"


class Assessment(UserScopedContract):
    """Auditable assessment against exact profile and job-profile revisions."""

    assessment_id: StableId
    assessment_type: AssessmentType
    job_id: StableId
    candidate_profile_id: StableId
    candidate_profile_revision: PositiveRevision
    job_profile_id: StableId
    job_profile_revision: PositiveRevision
    score: AssessmentScore
    confidence: ConfidenceScore
    strengths: list[NonEmptyText] = Field(default_factory=list)
    gaps: list[NonEmptyText] = Field(default_factory=list)
    risks: list[NonEmptyText] = Field(default_factory=list)
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    agent_run_id: StableId
    assessed_at: UtcTimestamp


class Recommendation(UserScopedContract):
    """A ranked job recommendation reproducible from its recorded inputs."""

    recommendation_id: StableId
    job_id: StableId
    candidate_profile_id: StableId
    candidate_profile_revision: PositiveRevision
    job_profile_id: StableId
    job_profile_revision: PositiveRevision
    assessment_ids: list[StableId] = Field(min_length=1)
    final_score: AssessmentScore
    rank: Annotated[int, Field(ge=1)]
    classification: RecommendationClassification
    explanation: NonEmptyText
    ranking_version: NonEmptyText
    created_at: UtcTimestamp


class UserFeedback(UserScopedContract):
    """A user's explicit response to a global job or its recommendation."""

    feedback_id: StableId
    job_id: StableId
    action: FeedbackAction
    reason: NonEmptyText | None = None
    free_text: NonEmptyText | None = None
    created_at: UtcTimestamp
