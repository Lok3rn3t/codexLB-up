# Verification

Source adaptation: upstream PR #2569 at
`778e10f4ab7111c7ab5539b448df2763fabc1987`.

Before implementation, the updated product-route test
`tests/integration/test_proxy_responses.py::test_backend_responses_preserves_non_message_developer_directive`
failed on baseline `3a6b118`: the forwarded `instructions` was
`follow the directive`, rather than empty. The developer message was hoisted.
The route test now covers both `/backend-api/codex/responses` and `/v1/responses`.

After implementation, running `tests/unit/test_openai_requests.py`,
`tests/unit/test_chat_request_mapping.py`,
`tests/unit/test_passthrough_request_fields.py`, and
`tests/integration/test_proxy_responses.py` produced **471 passed, 9 failed**
in 128 seconds on Windows/Python 3.13. The nine failures are the existing
`test_passthrough_nesting_at_the_limit_is_accepted_and_serializable` cases,
reporting Pydantic `Maximum serialization depth exceeded`. Re-executing the
baseline HEAD `app/core/openai/requests.py` in an isolated Python process and
rerunning just that test family reproduced the same **9 failed, 3 passed**.
No production source files were reverted for this baseline comparison. This
change does not modify the depth limit or serialization behavior. Linux CI
must still confirm the platform-specific cases before release.

A focused rerun of the three unit files excluding that pre-existing depth family
passed **361 tests** (12 depth cases deselected).

Ruff check and format check passed for all four changed Python files.
`npx --yes @fission-ai/openspec@1.11.0 validate preserve-developer-input-context --strict`
passed. Canonical requirement and rationale were synced.

No live OpenAI or production container requests were made.
