"""Deterministic recommendation ranking; no ranking arithmetic is delegated to an LLM."""

from src.domain.contracts import Assessment, RecommendationClassification


def rank_assessments(
    assessments: list[Assessment],
) -> list[tuple[Assessment, int, RecommendationClassification]]:
    """Rank jobs by the mean FIT/CAREER score, then job ID for stable ties."""
    by_job: dict[object, list[Assessment]] = {}
    for assessment in assessments:
        by_job.setdefault(assessment.job_id, []).append(assessment)
    ordered = sorted(
        by_job.values(),
        key=lambda group: (-sum(item.score for item in group) / len(group), str(group[0].job_id)),
    )
    ranked = []
    for rank, group in enumerate(ordered, start=1):
        score = round(sum(item.score for item in group) / len(group))
        classification = (
            RecommendationClassification.PRIORITY
            if score >= 75
            else RecommendationClassification.CONSIDER
            if score >= 50
            else RecommendationClassification.EXCLUDE
        )
        ranked.append((group[0], rank, classification))
    return ranked
