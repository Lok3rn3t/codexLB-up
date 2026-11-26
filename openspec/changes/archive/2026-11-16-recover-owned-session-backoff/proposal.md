## Why

A hard continuation owner in transient error backoff can produce repeated `previous_response_owner_unavailable` or `No available accounts` even when that ACTIVE account has quota. Its required-owner pool has one member, while the existing fallback requires another backed-off or unavailable member.

## What Changes

- Carry an explicit hard-owner-pool condition through existing selection paths.
- Allow the existing bounded-backoff fallback to admit that same owner without clearing health evidence.
- Preserve status, quota, file ownership, scope, security, concurrency, and caller-exclusion gates.
- Prove same-owner recovery and refusal of genuinely unavailable owners on both Responses HTTP routes.

## Capabilities

### Modified Capabilities

- `sticky-session-operations`: required-owner availability during transient backoff.

## Impact

Four existing balancer implementation files and selector/HTTP regressions. No setting, database migration, deployment, or change to history portability. Adapted from upstream PR #2627 at `d53b271e0a96cd33de479b732c0a0a9162fdf6aa`, whose selector implementation originates in #2486.
