"""Greenhouse public-board connector; source-specific code stays here."""

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol
from uuid import uuid4

from src.domain.contracts import RawJob


class GreenhouseHttpClient(Protocol):
    async def get_json(self, url: str) -> Mapping[str, object]: ...


@dataclass(frozen=True)
class GreenhouseBoard:
    token: str


class GreenhouseConnector:
    def __init__(
        self,
        client: GreenhouseHttpClient,
        *,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._client = client
        self._now = now

    async def fetch(self, board: GreenhouseBoard) -> list[RawJob]:
        payload = await self._client.get_json(
            f"https://boards-api.greenhouse.io/v1/boards/{board.token}/jobs?content=true"
        )
        source_jobs = payload.get("jobs")
        if not isinstance(source_jobs, list):
            raise TypeError("Greenhouse payload must contain a jobs list")
        retrieved_at = self._now()
        jobs: list[RawJob] = []
        for item in source_jobs:
            if not isinstance(item, dict):
                continue
            content = item.get("content") or ""
            title = item.get("title") or ""
            company = item.get("company_name") or board.token
            if not title or not content or not item.get("id") or not item.get("absolute_url"):
                continue
            location = (item.get("location") or {}).get("name")
            if not isinstance(location, str):
                location = None
            content_hash = sha256(
                json.dumps(
                    {
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": content,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()
            jobs.append(
                RawJob(
                    raw_job_id=uuid4(),
                    source_name="greenhouse",
                    external_id=str(item["id"]),
                    source_url=item["absolute_url"],
                    retrieved_at=retrieved_at,
                    published_at=item.get("first_published"),
                    updated_at=item.get("updated_at"),
                    title=title,
                    company_name=company,
                    location=location,
                    description=content,
                    source_payload=item,
                    content_hash=content_hash,
                )
            )
        return jobs
