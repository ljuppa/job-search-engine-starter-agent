"""Deterministic eligibility and score arithmetic for current-fit assessments."""

from dataclasses import dataclass

from src.domain.contracts import CandidateProfile, JobProfile


@dataclass(frozen=True)
class ConstraintResult:
    eligible: bool
    failures: tuple[str, ...]
    unknowns: tuple[str, ...]


def evaluate_constraints(profile: CandidateProfile, job: JobProfile) -> ConstraintResult:
    failures: list[str] = []
    unknowns: list[str] = []
    role_text = " ".join(filter(None, [job.role_family, job.seniority])).casefold()
    if profile.excluded_roles and any(role.casefold() in role_text for role in profile.excluded_roles):
        failures.append("job matches an excluded role")
    if profile.work_model_preferences.acceptable_models:
        if job.work_model is None:
            unknowns.append("job work model is unknown")
        elif job.work_model not in profile.work_model_preferences.acceptable_models:
            failures.append("job work model is not acceptable")
    if profile.location_preferences.preferred_locations:
        if job.location is None:
            unknowns.append("job location is unknown")
        elif not any(location.casefold() in job.location.casefold() for location in profile.location_preferences.preferred_locations):
            failures.append("job location is not acceptable")
    minimum = profile.compensation_preferences.minimum_annual_amount
    maximum = job.compensation.maximum_annual_amount
    if minimum is not None:
        if maximum is None:
            unknowns.append("job compensation is unknown")
        elif maximum < minimum:
            failures.append("job maximum compensation is below profile minimum")
    if profile.hard_constraints:
        unknowns.append("free-text hard constraints require explicit review")
    return ConstraintResult(eligible=not failures, failures=tuple(failures), unknowns=tuple(unknowns))


def calculate_score(*, constraints: ConstraintResult, strengths: int, gaps: int, risks: int) -> int:
    if not constraints.eligible:
        return 0
    return max(0, min(100, 50 + strengths * 10 - gaps * 12 - risks * 8 - len(constraints.unknowns) * 3))
