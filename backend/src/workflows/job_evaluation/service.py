"""Explicit Scout/Analyst/Matcher/Strategist composition boundary for one job."""

from dataclasses import dataclass
from uuid import uuid4

from src.agents.analyst import AnalystInput
from src.agents.matcher import MatcherInput
from src.agents.strategist import StrategistInput
from src.domain.contracts import (
    Assessment,
    CandidateProfile,
    ExecutionContext,
    ExecutionScope,
    Job,
    JobProfile,
    RawJob,
)


@dataclass(frozen=True)
class JobEvaluationResult:
    job_profile: JobProfile
    fit_assessment: Assessment
    career_assessment: Assessment


class JobEvaluationWorkflow:
    """Coordinates agents explicitly; agents never know about one another."""

    def __init__(self, analyst, matcher, strategist) -> None:
        self._analyst = analyst
        self._matcher = matcher
        self._strategist = strategist

    async def run(
        self,
        *,
        context: ExecutionContext,
        raw_job: RawJob,
        job: Job,
        candidate_profile: CandidateProfile,
    ) -> JobEvaluationResult:
        analyst_context = ExecutionContext(
            correlation_id=context.correlation_id,
            trace_id=context.trace_id,
            workflow_run_id=context.workflow_run_id,
            scope=ExecutionScope.GLOBAL,
            job_id=job.job_id,
        )
        analyst_input = AnalystInput(
            context=analyst_context, raw_job=raw_job, job=job, prompt_version="analyst.extract.v1"
        )
        job_profile = await self._analyst.run(analyst_input)
        matcher_input = MatcherInput(
            context=context,
            candidate_profile=candidate_profile,
            job_profile=job_profile,
            agent_run_id=uuid4(),
            prompt_version="matcher.v1",
        )
        fit_assessment = await self._matcher.run(matcher_input)
        strategist_input = StrategistInput(
            context=context,
            candidate_profile=candidate_profile,
            job_profile=job_profile,
            agent_run_id=uuid4(),
            prompt_version="strategist.v1",
        )
        career_assessment = await self._strategist.run(strategist_input)
        return JobEvaluationResult(job_profile, fit_assessment, career_assessment)
