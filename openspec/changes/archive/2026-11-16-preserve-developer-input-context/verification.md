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

## Current-head Linux validation

Candidate `466dd50df24110792eeb7addfdcc987e7dd3aeed` passed the complete CI workflow:
https://github.com/Lok3rn3t/codexLB-up/actions/runs/43929436577

The unit slice passed 10,739 tests (7 documented skips, 1 existing expected
failure), including serialization-depth and proxy environment cases that fail
on the unchanged Windows baseline. The native wire suite passed 374 tests,
including real-worker receive-credit regressions. All integration slices,
PostgreSQL, migration, frontend, package, Docker, Helm, Nix, type and lint gates
passed. Five legacy idle-loss fixtures were updated to the real typed message
after initial CI identified a missing error attribute; their lifecycle
assertions are unchanged. No production deployment was performed.
