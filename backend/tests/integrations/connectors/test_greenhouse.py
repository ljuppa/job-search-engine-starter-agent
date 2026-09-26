import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.integrations.connectors.greenhouse import GreenhouseBoard, GreenhouseConnector


class FrozenClient:
    async def get_json(self, url: str):
        assert url == "https://boards-api.greenhouse.io/v1/boards/example/jobs?content=true"
        fixture = (
            Path(__file__).parents[4]
            / "evals/datasets/frozen_jobs/greenhouse/public_board_jobs.json"
        )
        return json.loads(fixture.read_text())


@pytest.mark.asyncio
async def test_greenhouse_connector_parses_frozen_public_board_payload() -> None:
    connector = GreenhouseConnector(FrozenClient(), now=lambda: datetime(2026, 9, 26, tzinfo=UTC))

    jobs = await connector.fetch(GreenhouseBoard(token="example"))

    assert [job.external_id for job in jobs] == ["101", "102"]
    assert jobs[0].company_name == "example"
    assert jobs[0].published_at == datetime(2026, 9, 1, 9, tzinfo=UTC)
    assert jobs[0].content_hash != jobs[1].content_hash


@pytest.mark.asyncio
async def test_greenhouse_connector_rejects_malformed_payload() -> None:
    class InvalidClient:
        async def get_json(self, url: str):
            return {"jobs": "not-a-list"}

    with pytest.raises(TypeError, match="jobs list"):
        await GreenhouseConnector(InvalidClient()).fetch(GreenhouseBoard(token="example"))
