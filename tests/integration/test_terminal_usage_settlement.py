from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select

from app.core.openai.models import CompactResponsePayload, OpenAIEvent
from app.core.types import JsonValue
from app.db.models import Account, RequestLog
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.api_keys.repository import ApiKeysRepository
from app.modules.api_keys.service import ApiKeyCreateData, ApiKeyRequestUsageBudget, ApiKeysService, LimitRuleInput
from app.modules.proxy import service as proxy_service
from tests.integration.test_proxy_api_extended import _import_account

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["websocket", "compact"])
@pytest.mark.parametrize("status", ["completed", "failed", "incomplete"])
@pytest.mark.parametrize(
    ("input_tokens", "output_tokens"),
    [(100, 50), (0, 0), (None, None), (100, None), (None, 50)],
)
async def test_terminal_reported_usage_settles_once(
    async_client, app_instance, surface: str, status: str, input_tokens: int | None, output_tokens: int | None
) -> None:
    account_id = await _import_account(async_client, "acc_terminal_usage", "terminal-usage@example.com")
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        api_keys = ApiKeysService(ApiKeysRepository(session))
        created = await api_keys.create_key(
            ApiKeyCreateData(
                name="terminal-usage",
                allowed_models=None,
                expires_at=None,
                limits=[
                    LimitRuleInput(limit_type=limit_type, limit_window="weekly", max_value=1_000)
                    for limit_type in ("input_tokens", "output_tokens", "total_tokens")
                ],
            )
        )
        api_key = await api_keys.get_key_by_id(created.id)
        reservation = await api_keys.enforce_limits_for_request(
            created.id,
            request_model="gpt-5.5",
            request_usage_budget=ApiKeyRequestUsageBudget(input_tokens=4, output_tokens=6),
        )
        assert reservation is not None

    usage: dict[str, JsonValue] | None = None
    if input_tokens is not None or output_tokens is not None:
        usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_tokens_details": {"cached_tokens": 40 if input_tokens else 0},
            "output_tokens_details": {"reasoning_tokens": 30 if output_tokens else 0},
        }
    response: dict[str, JsonValue] = {"id": "resp_terminal_usage", "status": status, "usage": usage}
    if status == "incomplete":
        response["incomplete_details"] = {"reason": "max_output_tokens"}
    service = get_proxy_service_for_app(app_instance)

    if surface == "websocket":
        payload: dict[str, JsonValue] = {"type": f"response.{status}", "response": response}
        await service._finalize_websocket_request_state(
            proxy_service._WebSocketRequestState(
                request_id="req_terminal_usage",
                model="gpt-5.5",
                service_tier=None,
                reasoning_effort=None,
                api_key_reservation=reservation,
                started_at=asyncio.get_running_loop().time(),
            ),
            account=account,
            account_id_value=account.id,
            event=OpenAIEvent.model_validate(payload),
            event_type=f"response.{status}",
            payload=payload,
            api_key=api_key,
            upstream_control=proxy_service._WebSocketUpstreamControl(),
            response_create_gate=asyncio.Semaphore(1),
        )
        assert await service.drain_persistence_tasks(timeout_seconds=5)
        # Exercise the real reservation CAS after a duplicate terminal handoff.
        assert await service._settle_stream_api_key_usage(
            api_key,
            reservation,
            proxy_service._StreamSettlement(
                status="success" if status == "completed" else "error",
                model="gpt-5.5",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_input_tokens=40 if input_tokens else 0,
            ),
            request_id="resp_terminal_usage",
            wait_for_settlement=True,
        )
    else:
        compact_response = CompactResponsePayload.model_validate({"object": "response.compaction", **response})
        for _ in range(2):
            await service._settle_compact_api_key_usage(
                api_key=api_key,
                api_key_reservation=reservation,
                response=compact_response,
                request_service_tier=None,
            )
    assert await service.drain_persistence_tasks(timeout_seconds=5)

    complete_usage = input_tokens is not None and output_tokens is not None
    async with SessionLocal() as session:
        repo = ApiKeysRepository(session)
        stored = await repo.get_usage_reservation(reservation.reservation_id)
        limits = await repo.get_limits_by_key(created.id)
        if surface == "websocket":
            log = (await session.execute(select(RequestLog).where(RequestLog.account_id == account_id))).scalar_one()
            assert log.status == ("success" if status == "completed" else "error")
            assert log.input_tokens == input_tokens
            assert log.output_tokens == output_tokens
            expected_cached = (40 if input_tokens else 0) if usage else None
            expected_reasoning = (30 if output_tokens else 0) if usage else None
            assert log.cached_input_tokens == expected_cached
            assert log.reasoning_tokens == expected_reasoning
    assert stored is not None
    assert stored.status == ("finalized" if complete_usage else "released")
    expected_input = input_tokens if complete_usage else 0
    expected_output = output_tokens if complete_usage else 0
    assert {limit.limit_type: limit.current_value for limit in limits} == {
        "input_tokens": expected_input,
        "output_tokens": expected_output,
        "total_tokens": (expected_input or 0) + (expected_output or 0),
    }
