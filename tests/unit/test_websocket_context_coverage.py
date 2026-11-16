from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import app.modules.proxy.service as proxy_service
from app.core.types import JsonValue
from tests.unit.test_proxy_utils import _repo_factory, _RequestLogsRecorder

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize("stored_covers_context", [False, True])
async def test_injected_anchor_snapshots_context_coverage_before_admission(monkeypatch, stored_covers_context: bool):
    service = proxy_service.ProxyService(_repo_factory(_RequestLogsRecorder()))
    stored_input: list[JsonValue] = [{"role": "user", "content": [{"type": "input_text", "text": "previous turn"}]}]
    continuity = proxy_service._WebSocketContinuityState(
        last_completed_response_id="resp_selected",
        last_completed_input_count=1,
        last_completed_input_prefix_fingerprint=proxy_service._fingerprint_input_items(stored_input),
        last_completed_input_covers_context=stored_covers_context,
    )

    async def reserve(*args, **kwargs):
        continuity.last_completed_response_id = "resp_concurrent"
        continuity.last_completed_input_covers_context = not stored_covers_context
        return None

    monkeypatch.setattr(proxy_service, "get_settings", lambda: SimpleNamespace(trace_channels=frozenset()))
    monkeypatch.setattr(service, "_refresh_websocket_api_key_policy", AsyncMock(return_value=None))
    monkeypatch.setattr(service, "_reserve_websocket_api_key_usage", reserve)

    prepared = await service._prepare_websocket_response_create_request(
        {
            "type": "response.create",
            "model": "gpt-5.1",
            "input": [*stored_input, {"role": "user", "content": [{"type": "input_text", "text": "follow-up"}]}],
        },
        headers={"session_id": "coverage-snapshot"},
        codex_session_affinity=True,
        openai_cache_affinity=True,
        sticky_threads_enabled=False,
        openai_cache_affinity_max_age_seconds=300,
        api_key=None,
        continuity_state=continuity,
    )

    assert prepared.request_state.proxy_injected_previous_response_id is True
    assert json.loads(prepared.text_data)["previous_response_id"] == "resp_selected"
    assert prepared.request_state.input_covers_anchor_context is stored_covers_context
