from __future__ import annotations

from datetime import timedelta

import pytest
from sqlalchemy import delete

from app.core.crypto import TokenEncryptor
from app.core.utils.time import utcnow
from app.db.models import Account, AccountStatus, RequestLog
from app.db.session import SessionLocal
from app.modules.accounts.repository import AccountsRepository
from app.modules.accounts.usage_rollup import run_fold_pass
from app.modules.accounts.usage_time_rollup import run_hourly_fold_pass

pytestmark = pytest.mark.integration


async def _seed_usage(requested_at) -> None:
    encryptor = TokenEncryptor()
    async with SessionLocal() as session:
        await AccountsRepository(session).upsert(
            Account(
                id="observed",
                email="observed@example.com",
                plan_type="plus",
                access_token_encrypted=encryptor.encrypt("access"),
                refresh_token_encrypted=encryptor.encrypt("refresh"),
                id_token_encrypted=encryptor.encrypt("id"),
                last_refresh=requested_at,
                status=AccountStatus.ACTIVE,
            )
        )
        for request_id, input_tokens, output_tokens, reasoning_tokens, cached in (
            ("complete", 100, 50, 30, 40),
            ("reasoning", 100, None, 30, None),
            ("missing", None, None, None, None),
            ("zero", 0, 0, 0, 0),
            ("output", None, 7, None, None),
            ("input", 9, None, None, None),
            ("reasoning-only", None, None, 3, None),
            ("cache-only", None, None, None, 4),
        ):
            session.add(
                RequestLog(
                    account_id="observed",
                    request_id=request_id,
                    conversation_id="observed-conversation",
                    model="gpt-5.1",
                    status="success" if input_tokens is not None else "error",
                    requested_at=requested_at,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    reasoning_tokens=reasoning_tokens,
                    cached_input_tokens=cached,
                )
            )
        await session.commit()


RAW_COVERAGE = {"completeRequests": 2, "partialRequests": 4, "missingRequests": 2, "unknownRequests": 0}
FOLDED_COVERAGE = {"completeRequests": 0, "partialRequests": 0, "missingRequests": 0, "unknownRequests": 8}


@pytest.mark.asyncio
async def test_observed_token_usage_is_consistent_across_dashboard_apis(async_client, db_setup):
    await _seed_usage(utcnow() - timedelta(minutes=2))

    response = await async_client.get("/api/request-logs", params={"limit": 20})
    assert response.status_code == 200
    entries = {entry["requestId"]: entry for entry in response.json()["requests"]}
    expected = {
        "complete": (150, "complete"),
        "reasoning": (130, "partial"),
        "missing": (None, "missing"),
        "zero": (0, "complete"),
        "output": (7, "partial"),
        "input": (9, "partial"),
        "reasoning-only": (3, "partial"),
        "cache-only": (None, "missing"),
    }
    assert {key: (row["tokens"], row["usageCompleteness"]) for key, row in entries.items()} == expected
    assert entries["reasoning"]["outputTokensRaw"] is None
    assert entries["reasoning"]["outputTokens"] == 30

    response = await async_client.get("/api/dashboard/overview")
    assert response.status_code == 200
    metrics = response.json()["summary"]["metrics"]
    assert metrics["tokens"] == 299
    assert metrics["tokenUsage"] == RAW_COVERAGE
    assert sum(point["v"] for point in response.json()["trends"]["tokens"]) == 299

    response = await async_client.get("/api/accounts")
    assert response.status_code == 200
    account = response.json()["accounts"][0]["requestUsage"]
    assert account["totalTokens"] == 299
    assert account["tokenUsage"] == RAW_COVERAGE

    response = await async_client.get("/api/conversations")
    assert response.status_code == 200
    conversation = response.json()["conversations"][0]
    assert conversation["totalTokens"] == 299
    assert conversation["tokenUsage"] == RAW_COVERAGE

    response = await async_client.get("/api/conversations/observed-conversation")
    assert response.status_code == 200
    model = response.json()["modelStats"][0]
    assert model["totalInputTokens"] + model["totalOutputTokens"] == 299
    assert model["tokenUsage"] == RAW_COVERAGE


@pytest.mark.asyncio
async def test_folded_usage_preserves_known_totals_and_discloses_unknown_coverage(async_client, db_setup):
    now = utcnow()
    old = now - timedelta(days=2)
    await _seed_usage(old)
    await run_fold_pass(now=now)
    await run_hourly_fold_pass(now=now)
    async with SessionLocal() as session:
        await session.execute(delete(RequestLog).where(RequestLog.requested_at == old))
        await session.commit()

    response = await async_client.get("/api/dashboard/overview")
    assert response.status_code == 200
    metrics = response.json()["summary"]["metrics"]
    assert metrics["requests"] == 8
    assert metrics["tokens"] == 299
    assert metrics["tokenUsage"] == FOLDED_COVERAGE
    assert sum(point["v"] for point in response.json()["trends"]["tokens"]) == 299

    response = await async_client.get("/api/accounts")
    assert response.status_code == 200
    account = response.json()["accounts"][0]["requestUsage"]
    assert account["totalTokens"] == 299
    assert account["tokenUsage"] == FOLDED_COVERAGE


@pytest.mark.asyncio
async def test_empty_activity_has_zero_tokens_and_empty_coverage(async_client, db_setup):
    response = await async_client.get("/api/dashboard/overview")
    assert response.status_code == 200
    metrics = response.json()["summary"]["metrics"]
    assert metrics["tokens"] == 0
    assert metrics["tokenUsage"] == dict.fromkeys(RAW_COVERAGE, 0)
