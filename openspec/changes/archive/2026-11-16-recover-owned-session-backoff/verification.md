## Implementation

The four production balancer files implement the same reviewed upstream #2627/#2486 selection change. `hard_owner_pool` reaches the existing transient-backoff fallback only after required-owner narrowing. The fallback selects the same candidate without erasing error evidence. Existing continuity/full-resend and idle WebSocket loss recovery remains unchanged.

## Red-before evidence

With the route tests added and all four production files still unchanged, the positive `/v1/responses` case failed with HTTP 502 instead of 200. Its synthetic logs showed `No available accounts`, `hard_affinity_saturated`, and `previous_response_owner_unavailable` after a rejected injected anchor. Thus the fork's existing continuation fixes did not already address this selector failure.

## Verified results

- Three selector unit modules plus the selected HTTP regression cases: **442 passed, 184 deselected** in 65.36 seconds. This includes all four newly added combinations of public/native Responses routes and transient-backoff/real-quota cases, plus other selected HTTP tests.
- Load-balancer integration module: **13 passed**.
- Scoped Ruff lint and formatting: clean across all eight implementation/test files.
- Scoped `ty check`: clean across the four implementation files.
- Strict change validation: passed.
- Strict canonical-spec validation: **67 passed**.
- `git diff --check`: clean for the affected files.

The positive HTTP cases use a generated isolated API key, real selection and health updates, isolated SQLite, and stub upstream sockets. They prove that an independent sibling session succeeds, the original owner is recovered with unchanged encrypted reasoning and completed tool history, the retired anchor is not re-injected, and later turn-state continuation succeeds. Negative cases prove real quota refusal and zero opaque-history dispatch to the sibling. Existing selector contract cases cover status, scope, policy, file-owner and exclusion restrictions; new core tests retain the counter/timestamp and healthy-sibling preference.

## Limits

These are synthetic regression results, not production deployment evidence. No live service logs, production database, credentials, client configuration, or production server were accessed or modified. The fix addresses transient backoff on an otherwise eligible hard owner; real quota exhaustion, unavailable credentials/accounts, absent ownership/history proof and unrelated upstream transport failures may still produce an owner-unavailable error. Cloud CI and release deployment are verified separately by the release workflow.
