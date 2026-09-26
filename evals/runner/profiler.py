"""Reusable deterministic evaluator for frozen Profiler output cases."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProfilerEvalCase:
    case_id: str
    expected_fact_paths: tuple[str, ...]
    required_source_ids: tuple[str, ...]
    forbidden_inferred_paths: tuple[str, ...]


def load_cases(case_directory: Path) -> list[ProfilerEvalCase]:
    return [
        ProfilerEvalCase(
            case_id=payload["case_id"], expected_fact_paths=tuple(payload["expected_fact_paths"]),
            required_source_ids=tuple(payload["required_source_ids"]),
            forbidden_inferred_paths=tuple(payload.get("forbidden_inferred_paths", [])),
        )
        for path in sorted(case_directory.glob("*.json"))
        for payload in [json.loads(path.read_text())]
    ]


def evaluate(case: ProfilerEvalCase, result: dict) -> list[str]:
    """Return deterministic failure messages; an empty list means the case passed."""

    facts = result.get("facts", [])
    paths = {fact.get("field_path") for fact in facts}
    failures = [f"missing expected fact: {path}" for path in case.expected_fact_paths if path not in paths]
    for fact in facts:
        if fact.get("field_path") in case.forbidden_inferred_paths and fact.get("disposition") == "INFERRED":
            failures.append(f"unsupported inference: {fact['field_path']}")
        if fact.get("field_path") in case.expected_fact_paths:
            missing = set(case.required_source_ids) - set(map(str, fact.get("source_ids", [])))
            if missing:
                failures.append(f"missing provenance for {fact['field_path']}: {sorted(missing)}")
    return failures
