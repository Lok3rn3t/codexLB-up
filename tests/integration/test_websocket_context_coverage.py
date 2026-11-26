from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import app.modules.proxy.api as proxy_api
import app.modules.proxy.service as proxy_service
from tests.integration.test_proxy_websocket_responses import (
    _assert_previous_response_not_found_error,
    _FakeUpstreamMessage,
    _SequencedUpstreamWebSocket,
    _websocket_settings,
)

pytestmark = pytest.mark.integration


def test_injected_anchor_cannot_promote_delta_to_full_context(app_instance, monkeypatch):
    def completion(response_id: str) -> list[_FakeUpstreamMessage]:
        return [
            _FakeUpstreamMessage(
                "text",
                text=json.dumps({"type": f"response.{phase}", "response": {"id": response_id, "status": status}}),
            )
            for phase, status in (("created", "in_progress"), ("completed", "completed"))
        ]

    first_upstream = _SequencedUpstreamWebSocket(
        [],
        deferred_message_batches=[
            completion("resp_delta"),
            completion("resp_injected"),
            [
                _FakeUpstreamMessage(
                    "text",
                    text=json.dumps(
                        {
                            "type": "error",
                            "error": {
                                "type": "invalid_request_error",
                                "code": "previous_response_not_found",
                                "message": "Previous response with id 'resp_injected' not found.",
                                "param": "previous_response_id",
                            },
                        }
                    ),
                )
            ],
        ],
    )
    replay_upstream = _SequencedUpstreamWebSocket([], deferred_message_batches=[completion("resp_context_lost")])
    connections = 0

    async def connect(self, headers, **kwargs):
        nonlocal connections
        connections += 1
        return SimpleNamespace(id="acct_coverage"), first_upstream if connections == 1 else replay_upstream

    monkeypatch.setattr(proxy_api, "_websocket_firewall_denial_response", AsyncMock(return_value=None))
    monkeypatch.setattr(proxy_api, "validate_proxy_api_key_authorization", AsyncMock(return_value=None))
    monkeypatch.setattr(
        proxy_service, "get_settings_cache", lambda: SimpleNamespace(get=AsyncMock(return_value=_websocket_settings()))
    )
    monkeypatch.setattr(proxy_service.ProxyService, "_connect_proxy_websocket", connect)
    monkeypatch.setattr(proxy_service.ProxyService, "_write_request_log", AsyncMock())

    messages = [
        {"role": "user", "content": [{"type": "input_text", "text": text}]}
        for text in ("first delta", "second delta", "injected follow-up", "final follow-up")
    ]
    with TestClient(app_instance) as client:
        with client.websocket_connect(
            "/backend-api/codex/responses", headers={"session_id": "context-coverage-chain"}
        ) as websocket:
            for previous_response_id, items in (("resp_original_history", messages[:2]), (None, messages[:3])):
                payload = {"type": "response.create", "model": "gpt-5.4", "instructions": "", "input": items}
                if previous_response_id is not None:
                    payload["previous_response_id"] = previous_response_id
                websocket.send_json(payload)
                assert websocket.receive_json()["type"] == "response.created"
                assert websocket.receive_json()["type"] == "response.completed"
            websocket.send_json(
                {
                    "type": "response.create",
                    "model": "gpt-5.4",
                    "instructions": "",
                    "previous_response_id": "resp_injected",
                    "input": messages,
                }
            )
            terminal = websocket.receive_json()
            while terminal["type"] == "codex.keepalive":
                terminal = websocket.receive_json()

    assert terminal["type"] == "response.failed"
    _assert_previous_response_not_found_error(terminal["response"]["error"])
    assert connections == 1
    assert replay_upstream.sent_text == []
    injected = json.loads(first_upstream.sent_text[1])
    assert injected["previous_response_id"] == "resp_delta"
    assert injected["input"] == messages[2:3]
    final = json.loads(first_upstream.sent_text[2])
    assert final["previous_response_id"] == "resp_injected"
