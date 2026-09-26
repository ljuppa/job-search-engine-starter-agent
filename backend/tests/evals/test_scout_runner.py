from pathlib import Path

from evals.runner.scout import evaluate, load_cases


def test_scout_runner_loads_and_evaluates_frozen_cases() -> None:
    cases = load_cases(Path(__file__).parents[3] / "evals/cases/scout")

    assert len(cases) == 2
    assert (
        evaluate(
            cases[0],
            {
                "source_name": "greenhouse",
                "item_count": 2,
                "external_ids": ["101", "102"],
                "replay_created_raw_jobs": 0,
            },
        )
        == []
    )
