# Evidence and implementation provenance

Client examined: [openai/codex rust-v0.169.0](https://github.com/openai/codex/tree/rust-v0.169.0), commit `d32063f96c2dff1dc96af839b3952abb6acfeda4`. `codex-rs/core/src/client.rs` constructs deltas in `get_incremental_items` and resets session continuation when `websocket_connection` sees a closed connection. `codex-rs/codex-api/src/endpoint/responses_websocket.rs` classifies the canonical `previous_response_not_found` code as retryable. That public signal must remain recognizable.

Reviewed implementation and regression coverage are adapted from upstream contributor work:

- [Soju06/codex-lb#2731](https://github.com/Soju06/codex-lb/pull/2731), `43c65d67cba086d58c6ae763c83a86ea9bc027a3`: require evidence before replaying unknown anchors. This also fails closed for unknown empty-prewarm anchors described in #2574/#2575.
- [Soju06/codex-lb#2581](https://github.com/Soju06/codex-lb/pull/2581), `d83dac5b4fc1159a19fd539bc635e3425eecee9a`: preserve full agent context on the proven owner.
- [Soju06/codex-lb#2636](https://github.com/Soju06/codex-lb/pull/2636), `fa9c673c9f712a3369948beca559a1f69b025ceb`: notify idle native connection loss and preserve newer anchors.

An unknown anchored body cannot be distinguished from a delta by item count or tool-pair shape. The safe fallback is a recognized error so Codex can retry its retained full history. Agent messages may carry encrypted account-owned content: a same-owner proof never grants permission to move them to another account. A prewarm-specific optimization from #2575 is unnecessary for the stronger unknown-anchor safety rule and is not included.

These changes do not prove the cause of any particular production error without request diagnostics. Dependency updates alone do not fix lost conversation anchors.
