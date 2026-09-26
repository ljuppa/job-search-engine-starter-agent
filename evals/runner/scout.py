"""Deterministic structural evaluator for frozen Scout connector cases."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScoutEvalCase:
    case_id: str
    source_name: str
    fixture: str
    expected_item_count: int
    expected_external_ids: tuple[str, ...]
    replay_is_idempotent: bool


def load_cases(case_directory: Path) -> list[ScoutEvalCase]:
    return [
        ScoutEvalCase(
            case_id=payload["case_id"],
            source_name=payload["source_name"],
            fixture=payload["fixture"],
            expected_item_count=payload["expected_item_count"],
            expected_external_ids=tuple(payload["expected_external_ids"]),
            replay_is_idempotent=payload["replay_is_idempotent"],
        )
        for path in sorted(case_directory.glob("*.json"))
        for payload in [json.loads(path.read_text())]
    ]


def evaluate(case: ScoutEvalCase, result: dict) -> list[str]:
    """Return deterministic failures for a connector/ingestion execution summary."""
    failures: list[str] = []
    if result.get("source_name") != case.source_name:
        failures.append(f"wrong source: {result.get('source_name')}")
    if result.get("item_count") != case.expected_item_count:
        failures.append(f"wrong item count: {result.get('item_count')}")
    if tuple(map(str, result.get("external_ids", []))) != case.expected_external_ids:
        failures.append("wrong external ids")
    if case.replay_is_idempotent and result.get("replay_created_raw_jobs") != 0:
        failures.append("replay was not idempotent")
    return failures
