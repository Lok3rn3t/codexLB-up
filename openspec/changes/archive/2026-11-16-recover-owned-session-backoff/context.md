## Provenance and scope

Adapted from [upstream PR #2627](https://github.com/Soju06/codex-lb/pull/2627), head `d53b271e0a96cd33de479b732c0a0a9162fdf6aa`. The production selector implementation and selector tests originate in [PR #2486](https://github.com/Soju06/codex-lb/pull/2486); #2627 supplies the native HTTP route reproduction and explicit contract.

## Rationale and example

An ACTIVE account A with quota can enter transient-error backoff after upstream failures. A hard continuation narrows selection to A, making the existing fallback's comparison against other pool members impossible. The explicit condition admits A through the existing fallback and preserves its error count and timestamp. An independent session may still select healthy account B. A complete history containing encrypted reasoning and settled tool calls remains on A and is forwarded unchanged after an injected anchor is denied and retired.

## Constraints and limits

Real quota exhaustion, paused/deactivated status, file ownership, scope, security restrictions, concurrency caps and caller exclusions remain enforced. This does not make opaque history portable to B, fabricate missing history, or solve every owner-unavailable error. Production logs were not required or accessed; validation uses isolated synthetic route fixtures, real selection and health handling, and stub upstream sockets. No production server, database, migration, or client configuration is changed.

The existing unknown-anchor/full-resend proof, agent-message handling, and idle WebSocket-loss fixes must remain intact.
