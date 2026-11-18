from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from app.core.usage.pricing import ModelPrice
from app.core.usage.pricing_catalog import encode_snapshot
from scripts import update_upstream_metadata as script


async def test_generation_preserves_unchanged_snapshot_and_fails_before_writing_partial_data(tmp_path, monkeypatch):
    path = tmp_path / "pricing.json"
    original = encode_snapshot({"gpt-test": ModelPrice(10, 50, 1)})
    path.write_text(original)
    monkeypatch.setattr(script, "BUNDLE_PATH", path)
    monkeypatch.setattr(script, "ROOT", tmp_path)
    monkeypatch.setattr(script.CodexVersionCache, "_fetch_latest_version", AsyncMock(return_value="1.2.3"))
    primary = {
        "openai": {
            "models": {
                "gpt-test": {"modalities": {"output": ["text"]}, "cost": {"input": 10, "output": 50, "cache_read": 1}}
            }
        }
    }
    secondary = {
        "gpt-test": {
            "litellm_provider": "openai",
            "mode": "chat",
            "input_cost_per_token": 1e-5,
            "output_cost_per_token": 5e-5,
            "cache_read_input_token_cost": 1e-6,
        }
    }
    model = {
        "slug": "new-model",
        "display_name": "New model",
        "visibility": "list",
        "shell_type": "shell_command",
        "supported_in_api": True,
        "context_window": 123456,
        "available_in_plans": ["plus"],
        "model_messages": {"instructions_template": "example"},
    }
    release_url = "https://raw.githubusercontent.com/openai/codex/rust-v1.2.3/codex-rs/models-manager/models.json"
    sources = {
        script.MODELS_DEV_URL: primary,
        script.LITELLM_URL: secondary,
        release_url: {
            "models": [
                model,
                {**model, "slug": "hidden", "visibility": "hide"},
                {**model, "slug": "workspace-only", "allow_only_chatgpt_workspace_executor": True},
                {**model, "slug": "specialty", "model_specialty": "specialized"},
            ]
        },
    }
    monkeypatch.setattr(script, "fetch", sources.__getitem__)
    await script.main()
    assert path.read_text() == original
    version_path = tmp_path / "app/core/clients/codex_version_snapshot.py"
    assert 'CODEX_VERSION = "1.2.3"' in version_path.read_text()
    catalog_path = tmp_path / "app/core/openai/codex_models_snapshot.json"
    previous_catalog = catalog_path.read_text()
    assert json.loads(previous_catalog) == {
        "source": release_url,
        "models": [{k: v for k, v in model.items() if k != "model_messages"}],
    }
    primary["openai"]["models"]["gpt-test"]["cost"]["input"] = 42
    sources[release_url] = {"models": []}
    with pytest.raises(ValueError, match="no public models"):
        await script.main()
    assert path.read_text() == original
    assert catalog_path.read_text() == previous_catalog

    def fail_secondary(url):
        if url == script.MODELS_DEV_URL:
            return primary
        raise ValueError("unavailable")

    monkeypatch.setattr(script, "fetch", fail_secondary)
    with pytest.raises(ValueError, match="unavailable"):
        await script.main()
    assert path.read_text() == original
    assert 'CODEX_VERSION = "1.2.3"' in version_path.read_text()


def test_fetch_rejects_oversized_response_before_json_parsing(monkeypatch):
    from io import BytesIO
    from unittest.mock import Mock

    response = BytesIO(b" " * 33 + b"{}")
    reader = Mock(wraps=response.read)
    response.read = reader
    monkeypatch.setattr(script, "MAX_CATALOG_BYTES", 32)
    monkeypatch.setattr(script, "urlopen", lambda *args, **kwargs: response)
    with pytest.raises(ValueError, match="metadata response too large"):
        script.fetch("https://example.com/prices.json")
    reader.assert_called_once_with(33)


def test_fetch_accepts_response_at_size_limit(monkeypatch):
    from io import BytesIO

    monkeypatch.setattr(script, "MAX_CATALOG_BYTES", 16)
    monkeypatch.setattr(script, "urlopen", lambda *args, **kwargs: BytesIO(b'{"models": []}  '))
    assert script.fetch("https://example.com/prices.json") == {"models": []}
