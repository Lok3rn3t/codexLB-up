## Why

Codex rust-v0.169.0 sends incremental input with `previous_response_id` when its previous request and output form a prefix of the next request. The proxy must not treat an unknown anchor's delta as full conversation history, keep a client connected after its idle upstream context disappeared, or reject a proven same-owner full resend solely because it ends in an agent message.

## What Changes

- Require a known, complete stored prefix before replaying client-anchored input without its anchor.
- Notify native Codex clients with WebSocket close 1012 when a completed idle upstream is lost, retiring only that physical connection's anchor.
- Recognize valid agent messages in durable same-owner full-resend proofs while preserving original input and prohibiting cross-account fallback.
- Preserve the canonical `previous_response_not_found` recovery signal and the public `/v1/responses` error contract.

## Capabilities

### Modified Capabilities
- `responses-api-compat`: preserve conversation and account ownership across native WebSocket and HTTP bridge reconnects.

## Impact

Proxy continuation state and replay eligibility, product-path regressions, and Responses compatibility specification. No new settings, migrations, external dependencies, or client-visible payload fields.
