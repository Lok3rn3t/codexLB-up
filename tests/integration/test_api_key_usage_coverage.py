from __future__ import annotations

from datetime import timedelta

import pytest

from app.core.usage.types import TokenUsageCoverage
from app.core.utils.time import utcnow
from app.db.session import SessionLocal
from app.modules.accounts.usage_rollup import run_fold_pass
from app.modules.api_keys.repository import ApiKeysRepository
from app.modules.request_logs.repository import RequestLogsRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_api_key_usage_coverage_preserves_counts_and_marks_folded_history_unknown(async_client) -> None:
    response = await async_client.post("/api/api-keys", json={"name": "coverage-main"})
    assert response.status_code == 200
    key_id = response.json()["id"]
    other_response = await async_client.post("/api/api-keys", json={"name": "coverage-other"})
    assert other_response.status_code == 200
    other_key_id = other_response.json()["id"]
    async with SessionLocal() as session:
        empty = await ApiKeysRepository(session).get_usage_summary_by_key_id(key_id)
        assert empty.request_count == empty.total_tokens == 0
        assert empty.token_usage == TokenUsageCoverage()

    now = utcnow()
    old = now - timedelta(days=2)
    async with SessionLocal() as session:
        logs = RequestLogsRepository(session)
        for request_id, requested_at, input_tokens, output_tokens, reasoning_tokens, cached_tokens in [
            ("complete", now, 100, 50, 30, 40),
            ("zero", now, 0, 0, 0, 0),
            ("partial", now, 100, None, 30, None),
            ("missing", now, None, None, None, None),
            ("old-complete", old, 10, 10, 5, None),
            ("old-partial", old, 20, None, 10, None),
            ("old-missing", old, None, None, None, None),
        ]:
            row = await logs.add_log(
                account_id=None,
                api_key_id=key_id,
                request_id=request_id,
                model="gpt-5.5",
                status="error" if output_tokens is None else "success",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                reasoning_tokens=reasoning_tokens,
                cached_input_tokens=cached_tokens,
                requested_at=requested_at,
                latency_ms=100,
                error_code=None,
                cost_usd=0.01,
            )
            if request_id == "old-complete":
                # Key usage retains soft-deleted billed history, unlike account summaries.
                row.deleted_at = now
                await session.commit()
        for request_id, target_key, kind in [
            ("warmup", key_id, "warmup"),
            ("other-key", other_key_id, "normal"),
        ]:
            await logs.add_log(
                account_id=None,
                api_key_id=target_key,
                request_id=request_id,
                model="gpt-5.5",
                status="success",
                input_tokens=777,
                output_tokens=777,
                requested_at=old,
                request_kind=kind,
                latency_ms=100,
                error_code=None,
                cost_usd=1.0,
            )

    async def read_summary():
        listing = await async_client.get("/api/api-keys")
        assert listing.status_code == 200
        return next(row["usageSummary"] for row in listing.json() if row["id"] == key_id)

    before = await read_summary()
    assert before == {
        "requestCount": 7,
        "totalTokens": 330,
        "cachedInputTokens": 40,
        "totalCostUsd": pytest.approx(0.07),
        "tokenUsage": {
            "completeRequests": 3,
            "partialRequests": 2,
            "missingRequests": 2,
            "unknownRequests": 0,
        },
    }
    assert await run_fold_pass(now=now) >= 1
    after = await read_summary()
    assert after.pop("tokenUsage") == {
        "completeRequests": 2,
        "partialRequests": 1,
        "missingRequests": 1,
        "unknownRequests": 3,
    }
    before.pop("tokenUsage")
    assert after == before
    async with SessionLocal() as session:
        summaries = await ApiKeysRepository(session).list_usage_summary_by_key([key_id])
        assert set(summaries) == {key_id}
        assert summaries[key_id].token_usage == TokenUsageCoverage(
            complete_requests=2, partial_requests=1, missing_requests=1, unknown_requests=3
        )
